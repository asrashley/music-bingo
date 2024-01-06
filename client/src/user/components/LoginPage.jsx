import React, { useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { reverse } from 'named-urls';
import { push } from '@lagunovsky/redux-react-router';

import { LoginDialog } from './LoginDialog';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import { routes } from '../../routes/routes';

import '../styles/user.scss';

export function LoginPage() {
  const user = useSelector(getUser);
  const dispatch = useDispatch();

  const changePage = useCallback(() => {
    dispatch(push(reverse(`${routes.index}`)));
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.loggedIn === true) {
      changePage();
    }
  }, [user, changePage]);

  const showWelcome = !user.isFetching && user.loggedIn;
  return (
    <div className={!user.loggedIn ? 'modal-open' : ''} id="login-page">
      {!user.loggedIn && <LoginDialog dispatch={dispatch} onSuccess={changePage}
        onCancel={changePage} user={user} />}
      {showWelcome && <p>
        Welcome {user.username}. You can now go to the
        <Link to={reverse(`${routes.index}`)}>home page</Link>
        and start playing!</p>}
    </div>
  );
}
