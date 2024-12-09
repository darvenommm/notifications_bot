import axios from 'axios';
import { FormEvent, useState } from 'react';
import { TextField, Button, Box, Typography } from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { isAfter } from 'date-fns';
import { useNavigate } from 'react-router';

import { IS_AUTH } from '../constants';

const enum FormState {
  NONE = 'none',
  PENDING = 'pending',
  ERROR = 'error',
  SUCCESS = 'success',
}

export const HomePage = (): JSX.Element => {
  const [message, setMessage] = useState<string>('');
  const [datetime, setDatetime] = useState<Date | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [errorDatetime, setErrorDatetime] = useState<string>('');
  const [errorForm, setErrorForm] = useState<string>('');
  const [state, setState] = useState<FormState>(FormState.NONE);

  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent): Promise<void> => {
    event.preventDefault();

    if (!message) {
      setErrorMessage('Сообщение обязательно');
    } else {
      setErrorMessage('');
    }

    if (!datetime || !isAfter(datetime, new Date())) {
      setErrorDatetime('Пожалуйста, выберите дату и время в будущем');
    } else {
      setErrorDatetime('');
    }

    const isCorrectData = message && datetime && isAfter(datetime, new Date());
    if (isCorrectData) {
      const isoDatetime = datetime.toISOString();

      setState(FormState.PENDING);
      setErrorForm('');

      try {
        await axios.post(
          `${import.meta.env.VITE_PROXY_URL}/notifications`,
          {
            message,
            datetime: isoDatetime,
          },
          {
            withCredentials: true,
          },
        );
        setState(FormState.SUCCESS);
      } catch (error) {
        if (
          error instanceof axios.AxiosError &&
          error.status === axios.HttpStatusCode.Unauthorized
        ) {
          localStorage.setItem(IS_AUTH, String(false));
          navigate('/auth');
        }

        setState(FormState.ERROR);
        setErrorForm('Какая-то ошибка на стороне сервера');
      }
    }
  };

  return (
    <Box sx={{ maxWidth: 400, margin: 'auto', padding: 2 }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Форма для уведомлений
      </Typography>
      <form onSubmit={handleSubmit}>
        {errorForm && (
          <Typography color="error" variant="body2" sx={{ marginTop: 1 }}>
            {errorForm}
          </Typography>
        )}
        <TextField
          fullWidth
          label="Message"
          variant="outlined"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          error={!!errorMessage}
          helperText={errorMessage}
          margin="normal"
        />
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <DateTimePicker
            label="Выберите дату и время"
            value={datetime}
            onChange={(newValue) => setDatetime(newValue)}
            minDateTime={new Date()}
          />
        </LocalizationProvider>
        {errorDatetime && (
          <Typography color="error" variant="body2" sx={{ marginTop: 1 }}>
            {errorDatetime}
          </Typography>
        )}
        <Button
          type="submit"
          disabled={state === FormState.PENDING}
          variant="contained"
          color="primary"
          fullWidth
          sx={{ marginTop: 2 }}
        >
          Отправить
        </Button>
      </form>
    </Box>
  );
};
