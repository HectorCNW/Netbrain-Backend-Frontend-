import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../../api';

interface Page { id: number; titulo: string; }

export default function ProjectPages({ projectId }: { projectId: number }) {
  const [pages, setPages] = useState<Page[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`/proyectos/${projectId}/paginas`).then(res => setPages(res.data)).catch(console.error);
  }, [projectId]);

  return (
    <List>
      {pages.map(p => (
        <ListItem key={p.id} secondaryAction={<Button onClick={() => navigate(`/pages/${p.id}`)}>Editar</Button>}>
          <ListItemText primary={p.titulo} />
        </ListItem>
      ))}
    </List>
  );
}
