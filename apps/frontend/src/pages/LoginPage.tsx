import axios from 'axios';
import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router';
import { TextField, Button, Container, Typography, Box, CircularProgress } from '@mui/material';

import { IS_AUTH } from '../constants';

interface Errors {
  username: boolean;
  password: boolean;
}

const enum FormState {
  NONE = 'none',
  PENDING = 'pending',
  ERROR = 'error',
  SUCCESS = 'success',
}

export const LoginPage = (): JSX.Element => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [state, setState] = useState<FormState>(FormState.NONE);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [errors, setErrors] = useState<Errors>({
    username: false,
    password: false,
  });

  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent): Promise<void> => {
    event.preventDefault();

    const isCorrectUsername = Boolean(username.trim().length);
    const isCorrectPassword = Boolean(password.trim().length);

    setErrors({
      username: !isCorrectUsername,
      password: !isCorrectPassword,
    });

    const isCorrectData = [isCorrectUsername, isCorrectPassword].every(Boolean);
    if (isCorrectData) {
      setState(FormState.PENDING);
      setErrorMessage('');

      try {
        await axios.post(
          `${import.meta.env.VITE_PROXY_URL}/auth`,
          { username, password },
          {
            withCredentials: true,
          },
        );

        setState(FormState.SUCCESS);
        window.localStorage.setItem(IS_AUTH, String(true));
        navigate('/');
      } catch {
        setState(FormState.ERROR);
        window.localStorage.setItem(IS_AUTH, String(false));
        setErrorMessage('Неверные данные, попробуйте снова');
      }
    }
  };

  return (
    <Container
      component="main"
      maxWidth="xs"
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
      }}
    >
      <Box
        sx={{
          width: '100%',
          padding: 3,
          backgroundColor: '#333',
          borderRadius: 2,
          boxShadow: 3,
        }}
      >
        <Typography variant="h5" component="h1" align="center" color="white" gutterBottom>
          Форма регистрации
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Username"
            variant="outlined"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            error={errors.username}
            helperText={errors.username ? 'Поле не может быть пустым' : ''}
            margin="normal"
            autoFocus
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            error={errors.password}
            helperText={errors.password ? 'Поле не может быть пустым' : ''}
            margin="normal"
          />
          {state === FormState.ERROR && (
            <Typography color="error" align="center" sx={{ marginTop: 2 }}>
              {errorMessage}
            </Typography>
          )}
          <Button
            fullWidth
            type="submit"
            variant="contained"
            color="primary"
            sx={{ marginTop: 2 }}
            disabled={state === FormState.PENDING}
          >
            {state === FormState.PENDING ? <CircularProgress size={24} color="inherit" /> : 'Войти'}
          </Button>
        </form>
      </Box>
    </Container>
  );
};
