import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { Welcome } from '../../app/Welcome';
import {
  fetchUserIfNeeded, checkGuestToken, createGuestAccount, loginUser,
  clearGuestDetails,
} from '../../user/userSlice';
import { getUser } from '../../user/userSelectors';
import routes from '../../routes';
import { gameInitialFields } from '../../games/gamesSlice';
import { ticketInitialState } from '../../tickets/ticketsSlice';
import { GamePropType } from '../../games/types/Game';
import { UserPropType } from '../types/User';
import { HistoryPropType } from '../../types/History';
import { TicketPropType } from '../../tickets/types/Ticket';

import '../styles/user.scss';

export class GuestAccessPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: GamePropType.isRequired,
    history: HistoryPropType.isRequired,
    ticket: TicketPropType.isRequired,
    token: PropTypes.string,
    user: UserPropType.isRequired
  };

  componentDidMount() {
    const { dispatch, token, user } = this.props;
    const { guest } = user;

    if (user.loggedIn === true) {
      this.changePage();
      return;
    }
    dispatch(fetchUserIfNeeded());
    dispatch(checkGuestToken(token));

    if (guest.username && guest.password) {
      return dispatch(loginUser({
        password: guest.password,
        username: guest.username,
        rememberme: false,
      }))
        .then(this.loginResponse);
    }
  }

  loginResponse = (result) => {
    const { dispatch } = this.props;
    const { payload } = result;
    if (payload && payload.accessToken) {
      this.changePage();
    } else {
      dispatch(clearGuestDetails());
    }
  };

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user, token } = this.props;
    if (prevProps.user.loggedIn !== user.loggedIn && user.loggedIn === true) {
      this.changePage();
    }
    else if (prevProps.token !== token) {
      dispatch(checkGuestToken(token));
    }
  }

  playAsGuest = () => {
    const { dispatch, token } = this.props;
    dispatch(createGuestAccount(token));
  };

  changePage = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  };

  render() {
    const { game, ticket, token, user } = this.props;
    const { guest } = user;
    let error = null;
    if (token === undefined || guest.valid === false) {
      error = (
        <React.Fragment>
          <p className="description alert alert-warning">Sorry, the link you have used is not recognised</p>
          <p className="description">Either double-check the guest link you recevied, login or create
            an account.</p>
        </React.Fragment>
      );
    }
    if (guest.isFetching === true || guest.valid === null) {
      error = (
        <h2 className="description">Checking if guest link is valid...</h2>
      );
    }
    if (error === null && guest.error) {
      error = (
        <div className="alert alert-warning" role="alert">
          <span className="error-message">{guest.error}</span>
        </div>
      );
    }
    return (
      <Welcome className="guest-link index-page" game={game} ticket={ticket}>
        {error}
        <p className="action-buttons mt-5">
          <Link to={reverse(`${routes.login}`)} className="login nav-link btn btn-success btn-lg login-button">Log in</Link>
          <Link to={reverse(`${routes.register}`)} className="login nav-link btn btn-success btn-lg login-button">Create an account</Link>
          {guest.valid === true && <button className="play-guest nav-link btn btn-primary btn-lg"
            onClick={this.playAsGuest}>Play as a guest</button>}
        </p>
      </Welcome>
    );
  };
}

const mapStateToProps = (state, ownProps) => {
  const { token } = ownProps.match.params;

  const now = new Date();
  const game = {
    ...gameInitialFields,
    id: `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`,
  };
  const ticket = {
    ...ticketInitialState(),
    number: 1 + now.getHours(),
  };
  return {
    game,
    ticket,
    token,
    user: getUser(state, ownProps),
  };
};

export const GuestAccessPage = connect(mapStateToProps)(GuestAccessPageComponent);
