import React, { useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import { reverse } from 'named-urls';
import { push } from '@lagunovsky/redux-react-router';

import { Welcome } from '../../app/Welcome';
import {
  fetchUserIfNeeded, checkGuestTokenIfNeeded, createGuestAccount, loginUser,
  clearGuestDetails,
} from '../../user/userSlice';
import { getUser } from '../../user/userSelectors';
import { routes } from '../../routes/routes';
import { gameInitialFields } from '../../games/gamesSlice';
import { ticketInitialState } from '../../tickets/ticketsSlice';
import { GuestPropType } from '../types/Guest';

import '../styles/user.scss';

function GuestStatusMessage({ token, guest }) {
  if (token === undefined || guest?.valid === false) {
    return (
      <React.Fragment>
        <p className="description alert alert-warning">Sorry, the link you have used is not recognized</p>
        <p className="description">Either double-check the guest link you received, login or create
          an account.</p>
      </React.Fragment>
    );
  }
  if (guest?.isFetching === true || guest?.valid === null) {
    return (
      <h2 className="description">Checking if guest link is valid...</h2>
    );
  }
  if (guest?.error) {
    return (
      <div className="alert alert-warning" role="alert">
        <span className="error-message">{guest.error}</span>
      </div>
    );
  }
  return null;
}

GuestStatusMessage.propTypes = {
  token: PropTypes.string,
  guest: GuestPropType,
};

export function GuestAccessPage({ nextPage = reverse(`${routes.index}`) }) {
  const [game, ticket] = useMemo(() => {
    const now = new Date();
    const fakeGame = {
      ...gameInitialFields,
      id: `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`,
    };
    const fakeTicket = {
      ...ticketInitialState(),
      number: 1 + now.getHours(),
    };
    return [fakeGame, fakeTicket];
  }, []);
  const { token } = useParams();
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const { guest } = user;

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.loggedIn === true) {
      dispatch(push(nextPage));
      return;
    }
  }, [dispatch, user.loggedIn, nextPage]);

  useEffect(() => {
    // TODO: check if token needs validation
    if (token) {
      dispatch(checkGuestTokenIfNeeded(token));
    }
  }, [dispatch, token]);

  const playAsGuest = async () => {
    if (!guest?.username || !guest?.password) {
      dispatch(createGuestAccount(token, nextPage));
      return;
    }
    const { payload } = await dispatch(loginUser({
      password: guest.password,
      username: guest.username,
      rememberme: false,
    }));
    if (payload && payload.accessToken) {
      dispatch(push(nextPage));
    } else {
      dispatch(clearGuestDetails());
    }
  };

  return (
    <Welcome className="guest-link index-page" game={game} ticket={ticket}>
      <GuestStatusMessage token={token} guest={guest} />
      <p className="action-buttons mt-5">
        <Link to={reverse(`${routes.login}`)} className="login nav-link btn btn-success btn-lg login-button">Log in</Link>
        <Link to={reverse(`${routes.register}`)} className="login nav-link btn btn-success btn-lg login-button">Create an account</Link>
        {guest.valid === true && <button className="play-guest nav-link btn btn-primary btn-lg"
          onClick={playAsGuest}>Play as a guest</button>}
      </p>
    </Welcome>
  );
}

GuestAccessPage.propTypes = {
  nextPage: PropTypes.string,
};
