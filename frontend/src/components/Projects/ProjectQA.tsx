import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText } from '@mui/material';
import api from '../../api';

interface QA { id: number; titulo: string; pregunta: string; }

export default function ProjectQA({ projectId }: { projectId: number }) {
  const [qas, setQas] = useState<QA[]>([]);

  useEffect(() => {
    api.get(`/proyectos/${projectId}/preguntas`).then(res => setQas(res.data)).catch(console.error);
  }, [projectId]);

  return (
    <List>
      {qas.map(q => (
        <ListItem key={q.id}>
          <ListItemText primary={q.titulo} secondary={q.pregunta} />
        </ListItem>
      ))}
    </List>
  );
}
