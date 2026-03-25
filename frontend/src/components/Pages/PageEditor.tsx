import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import MDEditor from '@uiw/react-md-editor';
import api from '../../api';

interface Page { id: number; titulo: string; contenidoMarkdown: string; }

export default function PageEditor() {
  const { id } = useParams<{ id: string }>();
  const [page, setPage] = useState<Page | null>(null);
  const [titulo, setTitulo] = useState('');
  const [contenido, setContenido] = useState('');
  const [mensaje, setMensaje] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    api.get(`/paginas/${id}`).then(res => {
      setPage(res.data);
      setTitulo(res.data.titulo);
      setContenido(res.data.contenidoMarkdown);
    }).catch(console.error);
  }, [id]);

  const handleSave = async () => {
    if (!id) return;
    try {
      await api.patch(`/paginas/${id}`, { titulo, contenidoMarkdown: contenido });
      setMensaje('Guardado correctamente.');
      setTimeout(() => setMensaje(''), 2000);
    } catch (e) {
      setMensaje('Error al guardar.');
    }
  };

  if (!page) return <Container sx={{ mt: 4 }}>Loading...</Container>;

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4">Editar página</Typography>
      <TextField label="Título" fullWidth value={titulo} onChange={e => setTitulo(e.target.value)} sx={{ mt: 2 }} />
      <Box sx={{ mt: 2 }}>
        <MDEditor value={contenido} onChange={(val = '') => setContenido(val)} />
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <Button variant="contained" onClick={handleSave}>Guardar</Button>
        <Button variant="outlined" onClick={() => navigate(-1)}>Volver</Button>
      </Box>
      {mensaje && <Typography>{mensaje}</Typography>}
    </Container>
  );
}
