import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Container, Tab, Tabs, Typography } from '@mui/material';
import api from '../../api';
import ProjectPages from './ProjectPages';
import ProjectPRs from './ProjectPRs';
import ProjectQA from './ProjectQA';
import ProjectNotes from './ProjectNotes';
import ProjectDocuments from './ProjectDocuments';

interface Project { id: number; nombre: string; descripcion: string; lenguajes: string[]; }

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    if (!id) return;
    api.get(`/proyectos/${id}`).then(res => setProject(res.data)).catch(console.error);
  }, [id]);

  if (!project) return <Container sx={{ mt: 4 }}>Loading...</Container>;

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>{project.nombre}</Typography>
      <Typography>{project.descripcion}</Typography>
      <Typography sx={{ mb: 2 }}>Lenguajes: {project.lenguajes.join(', ')}</Typography>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tab} onChange={(e, v) => setTab(v)}>
          <Tab label="Páginas" />
          <Tab label="PRs" />
          <Tab label="Q&A" />
          <Tab label="Notas" />
          <Tab label="Documentos" />
        </Tabs>
      </Box>
      {tab === 0 && <ProjectPages projectId={Number(id)} />}
      {tab === 1 && <ProjectPRs projectId={Number(id)} />}
      {tab === 2 && <ProjectQA projectId={Number(id)} />}
      {tab === 3 && <ProjectNotes projectId={Number(id)} />}
      {tab === 4 && <ProjectDocuments projectId={Number(id)} />}
    </Container>
  );
}
