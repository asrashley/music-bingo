import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded } from '../gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { TrackListing } from './TrackListing';
import { ModifyGame } from './ModifyGame';

import '../styles/games.scss';

class TrackListingPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    loggedIn: PropTypes.bool.isRequired,
    game: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch, gamePk } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
    dispatch(fetchDetailIfNeeded(gamePk));
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, gamePk } = this.props;
    if (prevProps.user.pk !== this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
    if (prevProps.game.placeholder !== this.props.game.placeholder) {
      dispatch(fetchDetailIfNeeded(gamePk));
    }
  }

  render() {
    const { dispatch, game, loggedIn, user } = this.props;
    return (
      <div id="track-listing-page" className={loggedIn ? '' : 'modal-open'}  >
        {user.groups.admin === true && <ModifyGame game={game} dispatch={dispatch} />}
        <TrackListing game={game} />
        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  const { gamePk } = ownProps.match.params;
  let game = state.games.games[gamePk];
  if (game === undefined) {
    game = {
      title: '',
      pk: -1,
      tracks: [],
      placeholder: true,
    };
  }
  return {
    loggedIn: userIsLoggedIn(state),
    game,
    gamePk,
    user,
  };
};

TrackListingPage = connect(mapStateToProps)(TrackListingPage);

export {
  TrackListingPage
};