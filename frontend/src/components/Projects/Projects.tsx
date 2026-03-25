import { useEffect, useState } from 'react';
import { Box, Button, Container, List, ListItem, ListItemText, TextField, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../../api';

interface Project { id: number; nombre: string; descripcion: string; lenguajes: string[]; }

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/proyectos').then(res => setProjects(res.data)).catch(e => console.error(e));
  }, []);

  const filtered = projects.filter(p => p.nombre.toLowerCase().includes(search.toLowerCase()));

  return (
    <Container sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Proyectos</Typography>
        <Button variant="contained" onClick={() => navigate('/projects/0')} disabled>
          + Nuevo Proyecto (pendiente)
        </Button>
      </Box>
      <TextField fullWidth value={search} onChange={e => setSearch(e.target.value)} label="Buscar proyecto" />
      <List>
        {filtered.map(p => (
          <ListItem key={p.id} secondaryAction={<Button onClick={() => navigate(`/projects/${p.id}`)}>Ver</Button>}>
            <ListItemText primary={p.nombre} secondary={`${p.descripcion} (Lenguajes: ${p.lenguajes?.join(', ') || '-'})`} />
          </ListItem>
        ))}
      </List>
    </Container>
  );
}
