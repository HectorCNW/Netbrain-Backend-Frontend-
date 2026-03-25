import { useState } from 'react';
import { TextField, Button, Container, Typography, Box, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../../api';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/auth/register', { nombre: name, email, password });
      navigate('/login');
    } catch (err: any) {
      const message = err?.response?.data;
      if (message) {
        if (typeof message === 'string') setError(message);
        else if (message?.email) setError(message.email.join(' '));
        else if (message?.nombre) setError(message.nombre.join(' '));
        else if (message?.password) setError(message.password.join(' '));
        else if (message?.detail) setError(message.detail);
        else setError(JSON.stringify(message));
      } else {
        setError('No se pudo registrar, revise los datos.');
      }
    }
  };

  return (
    <Container maxWidth="xs" sx={{ mt: 8 }}>
      <Typography variant="h5" gutterBottom>
        Register
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField label="Name" fullWidth margin="normal" required value={name} onChange={(e) => setName(e.target.value)} />
        <TextField label="Email" fullWidth margin="normal" required value={email} onChange={(e) => setEmail(e.target.value)} />
        <TextField label="Password" fullWidth margin="normal" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
          Register
        </Button>
      </Box>
    </Container>
  );
}
