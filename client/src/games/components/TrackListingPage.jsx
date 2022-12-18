import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { TrackListing } from './TrackListing';
import { ModifyGame } from './ModifyGame';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded, invalidateGameDetail } from '../gamesSlice';

import { getGameImportState, getGame } from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { initialState } from '../../app/initialState';
import routes from '../../routes';

import '../styles/games.scss';

class TrackListingPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    game: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch, game } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
    if (game.pk > 0) {
      dispatch(fetchDetailIfNeeded(game.pk));
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, game, user } = this.props;
    if (prevProps.user.pk !== user.pk && user.pk > 0) {
      dispatch(fetchGamesIfNeeded());
    }
    if (prevProps.game.pk !== game.pk && game.pk > 0) {
      dispatch(fetchDetailIfNeeded(game.pk));
    }
  }

  reloadDetail = (ev) => {
    const { dispatch, game } = this.props;
    ev.preventDefault();
    dispatch(invalidateGameDetail({ game }));
    dispatch(fetchDetailIfNeeded({ game }));
    return false;
  }

  onDelete = () => {
    const { history } = this.props;
    history.push(`${routes.pastGames}`);
  }

  render() {
    const { dispatch, game, user, importing } = this.props;
    return (
      <div id="track-listing-page" className={user.loggedIn ? '' : 'modal-open'}  >
        {user.groups.admin === true && <ModifyGame game={game} dispatch={dispatch}
          options={user.options} onDelete={this.onDelete}
          importing={importing}
          onReload={this.reloadDetail} />}
        <TrackListing game={game} reload={this.reloadDetail} />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    game: getGame(state, ownProps),
    user: getUser(state, ownProps),
    importing: getGameImportState(state),
  };
};

TrackListingPage = connect(mapStateToProps)(TrackListingPage);

export {
  TrackListingPage
};
