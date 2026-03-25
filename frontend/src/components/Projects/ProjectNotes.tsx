import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText } from '@mui/material';
import api from '../../api';

interface Note { id: number; titulo: string; contenidoMarkdown: string; }

export default function ProjectNotes({ projectId }: { projectId: number }) {
  const [notes, setNotes] = useState<Note[]>([]);

  useEffect(() => {
    api.get(`/proyectos/${projectId}/notas-importantes`).then(res => setNotes(res.data)).catch(console.error);
  }, [projectId]);

  return (
    <List>
      {notes.map(note => (
        <ListItem key={note.id}>
          <ListItemText primary={note.titulo} secondary={note.contenidoMarkdown} />
        </ListItem>
      ))}
    </List>
  );
}
