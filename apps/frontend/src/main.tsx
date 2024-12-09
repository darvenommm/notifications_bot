import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createTheme, ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter, Route, Routes } from 'react-router';

import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { IsLoginGuard } from './guards/IsLoginGuard';
import { IsNotLoginGuard } from './guards/IsNotLoginGuard';

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<IsLoginGuard />}>
            <Route index element={<HomePage />} />
          </Route>
          <Route path="/auth" element={<IsNotLoginGuard />}>
            <Route index element={<LoginPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
);
