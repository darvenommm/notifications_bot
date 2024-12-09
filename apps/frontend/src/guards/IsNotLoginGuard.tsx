import { Navigate, Outlet } from 'react-router';

import { IS_AUTH } from '../constants';

export const IsNotLoginGuard = (): JSX.Element => {
  if (window.localStorage.getItem(IS_AUTH) === 'true') {
    return <Navigate to="/" />;
  }

  return <Outlet />;
};
