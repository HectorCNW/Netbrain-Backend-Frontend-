"""
Servicio de exportación PDF usando WeasyPrint.
Convierte Markdown a HTML y después a PDF con cabeceras de metadatos.
"""
import io
import markdown
import bleach
from django.template.loader import render_to_string
from django.utils import timezone

# Etiquetas HTML permitidas tras renderizar Markdown
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "pre", "code", "blockquote", "hr",
    "table", "thead", "tbody", "tr", "th", "td",
    "ul", "ol", "li", "strong", "em", "del",
    "a", "img",
]
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
}

MD_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "nl2br"]


def _md_to_safe_html(contenido: str) -> str:
    """Convierte Markdown a HTML seguro."""
    raw_html = markdown.markdown(contenido, extensions=MD_EXTENSIONS)
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)


CSS_BASE = """
    @page { margin: 2cm 2.5cm; size: A4; }
    body { font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11pt; color: #1a1a1a; line-height: 1.6; }
    h1 { font-size: 22pt; color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; margin-top: 24px; }
    h2 { font-size: 16pt; color: #1e3a5f; margin-top: 20px; }
    h3 { font-size: 13pt; color: #334155; margin-top: 16px; }
    pre, code { background: #f1f5f9; font-family: 'Courier New', monospace; font-size: 9pt; }
    pre { padding: 12px; border-radius: 4px; overflow-x: auto; }
    code { padding: 2px 5px; border-radius: 3px; }
    blockquote { border-left: 4px solid #3b82f6; margin: 0; padding: 8px 16px; background: #eff6ff; color: #1e40af; }
    table { border-collapse: collapse; width: 100%; margin: 16px 0; }
    th { background: #1e3a5f; color: white; padding: 8px 12px; text-align: left; }
    td { padding: 7px 12px; border-bottom: 1px solid #e2e8f0; }
    tr:nth-child(even) td { background: #f8fafc; }
    .meta { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; margin-bottom: 24px; border-radius: 6px; font-size: 10pt; color: #475569; }
    .meta strong { color: #0f172a; }
    .page-title { background: #1e3a5f; color: white; padding: 16px 20px; margin-bottom: 20px; border-radius: 6px; }
    .page-separator { border: none; border-top: 2px dashed #cbd5e1; margin: 36px 0; }
    .tag { display: inline-block; background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 10px; font-size: 9pt; margin-right: 4px; }
    .version-badge { display: inline-block; background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 10px; font-size: 9pt; }
    .no-tocar { background: #fef2f2; border-left: 4px solid #ef4444; padding: 8px 16px; margin: 8px 0; }
    .funcion-clave { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 8px 16px; margin: 8px 0; }
"""


def exportar_pagina_pdf(pagina) -> bytes:
    """Genera el PDF de una sola página wiki."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise RuntimeError("WeasyPrint no está instalado. Ejecuta: pip install weasyprint")

    html_contenido = _md_to_safe_html(pagina.contenido_markdown)
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (pagina.tags or []))

    html = f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
    <title>{pagina.titulo}</title></head><body>
    <div class="page-title"><h1 style="color:white;margin:0;">{pagina.titulo}</h1></div>
    <div class="meta">
        <strong>Proyecto:</strong> {pagina.proyecto.nombre} &nbsp;|&nbsp;
        <strong>Creado por:</strong> {pagina.creado_por.nombre if pagina.creado_por else '—'} &nbsp;|&nbsp;
        <strong>Última edición:</strong> {pagina.ultima_edicion_por.nombre if pagina.ultima_edicion_por else '—'} &nbsp;|&nbsp;
        <span class="version-badge">v{pagina.version_actual}</span> &nbsp;|&nbsp;
        <strong>Exportado:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}<br>
        <strong>Tags:</strong> {tags_html or '—'}
    </div>
    {html_contenido}
    </body></html>
    """

    buf = io.BytesIO()
    HTML(string=html).write_pdf(buf, stylesheets=[CSS(string=CSS_BASE)])
    return buf.getvalue()


def exportar_proyecto_pdf(proyecto) -> bytes:
    """Genera un PDF compilado con todas las páginas del proyecto."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        raise RuntimeError("WeasyPrint no está instalado. Ejecuta: pip install weasyprint")

    paginas = proyecto.paginas.select_related("creado_por", "ultima_edicion_por").order_by("titulo")

    secciones = []
    for i, pagina in enumerate(paginas):
        html_contenido = _md_to_safe_html(pagina.contenido_markdown)
        separador = '<hr class="page-separator">' if i > 0 else ""
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in (pagina.tags or []))
        secciones.append(f"""
            {separador}
            <h2>{pagina.titulo}</h2>
            <div class="meta">
                <strong>Autor:</strong> {pagina.creado_por.nombre if pagina.creado_por else '—'} &nbsp;|&nbsp;
                <strong>Última edición:</strong> {pagina.ultima_edicion_por.nombre if pagina.ultima_edicion_por else '—'} &nbsp;|&nbsp;
                <span class="version-badge">v{pagina.version_actual}</span> &nbsp;|&nbsp;
                <strong>Tags:</strong> {tags_html or '—'}
            </div>
            {html_contenido}
        """)

    colaboradores_html = ", ".join(
        f"{c.usuario.nombre} ({c.rol_en_proyecto})"
        for c in proyecto.colaboradores.select_related("usuario")
    )
    lenguajes_html = " · ".join(proyecto.lenguajes or [])

    html = f"""
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
    <title>{proyecto.nombre} — Documentación</title></head><body>
    <div class="page-title">
        <h1 style="color:white;margin:0 0 6px 0;">{proyecto.nombre}</h1>
        <p style="color:#bfdbfe;margin:0;font-size:10pt;">{proyecto.descripcion or ''}</p>
    </div>
    <div class="meta">
        <strong>Owner:</strong> {proyecto.owner.nombre} &nbsp;|&nbsp;
        <strong>Estado:</strong> {proyecto.estado} &nbsp;|&nbsp;
        <strong>Lenguajes:</strong> {lenguajes_html or '—'}<br>
        <strong>Colaboradores:</strong> {colaboradores_html or '—'}<br>
        <strong>Exportado:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')} &nbsp;|&nbsp;
        <strong>Total páginas:</strong> {paginas.count()}
    </div>
    {''.join(secciones) if secciones else '<p><em>Este proyecto no tiene páginas documentadas aún.</em></p>'}
    </body></html>
    """

    buf = io.BytesIO()
    HTML(string=html).write_pdf(buf, stylesheets=[CSS(string=CSS_BASE)])
    return buf.getvalue()
