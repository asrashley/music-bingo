import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

/* actions */
import {
  fetchUserIfNeeded, checkGuestToken, createGuestAccount, loginUser,
  clearGuestDetails,
} from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import routes from '../../routes';
import { gameInitialFields } from '../../games/gamesSlice';

import '../styles/user.scss';

class GuestAccessPage extends React.Component {
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
  }

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
      <div className="guest-link index-page">
        <div className="logo" />
        <div className="welcome">
          <h2 className="strapline">Like normal Bingo, but with music!</h2>
          <p className="description">Musical Bingo is a variation on the normal game of bingo, where the numbers are replaced
          with songs that the players must listen out for.</p>
          <p className="description">
            You can create an account to play Musical Bingo, or play as a guest.
            It is free and we won't pass on your details to anyone else.
            </p>
          {error}
          <p className="action-buttons mt-5">
            <Link to={reverse(`${routes.login}`)} className="login nav-link btn btn-success btn-lg login-button">Log in</Link>
            <Link to={reverse(`${routes.register}`)} className="login nav-link btn btn-success btn-lg login-button">Create an account</Link>
            {guest.valid === true && <button className="play-guest nav-link btn btn-primary btn-lg"
              onClick={this.playAsGuest}>Play as a guest</button>}
          </p>
        </div>
        <div className="number footer">Game {game.id} / Ticket {ticket.number}</div>
      </div>
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
    number: 1 + now.getHours(),
  };
  return {
    game,
    ticket,
    token,
    user: getUser(state, ownProps),
  };
};



GuestAccessPage = connect(mapStateToProps)(GuestAccessPage);

export {
  GuestAccessPage
};
