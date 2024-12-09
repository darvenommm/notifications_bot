import { Navigate, Outlet } from 'react-router';

import { IS_AUTH } from '../constants';

export const IsLoginGuard = (): JSX.Element => {
  if ((window.localStorage.getItem(IS_AUTH) ?? 'false') === 'false') {
    return <Navigate to="/auth" />;
  }

  return <Outlet />;
};
