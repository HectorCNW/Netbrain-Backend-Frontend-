import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText, Button } from '@mui/material';
import api from '../../api';

interface Doc { id: number; nombre: string; urlArchivo: string; }

export default function ProjectDocuments({ projectId }: { projectId: number }) {
  const [docs, setDocs] = useState<Doc[]>([]);

  useEffect(() => {
    api.get(`/proyectos/${projectId}/documentos`).then(res => setDocs(res.data)).catch(console.error);
  }, [projectId]);

  return (
    <List>
      {docs.map(doc => (
        <ListItem key={doc.id} secondaryAction={<Button href={doc.urlArchivo} target="_blank">Download</Button>}>
          <ListItemText primary={doc.nombre} />
        </ListItem>
      ))}
    </List>
  );
}
