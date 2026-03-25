import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText } from '@mui/material';
import api from '../../api';

interface PR { id: number; titulo: string; estado: string; }

export default function ProjectPRs({ projectId }: { projectId: number }) {
  const [prs, setPrs] = useState<PR[]>([]);

  useEffect(() => {
    api.get(`/proyectos/${projectId}/github/prs`).then(res => setPrs(res.data)).catch(console.error);
  }, [projectId]);

  return (
    <List>
      {prs.map(pr => (
        <ListItem key={pr.id}>
          <ListItemText primary={pr.titulo} secondary={pr.estado} />
        </ListItem>
      ))}
    </List>
  );
}
