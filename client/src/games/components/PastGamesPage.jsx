import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { PopularityGraph } from './PopularityGraph';
import { AdminGameActions } from './AdminGameActions';

import { fetchUserIfNeeded } from '../../user/userSlice';
import {
  fetchGamesIfNeeded, invalidateGames, setPopularityOptions,
} from '../gamesSlice';

import { getLocation } from '../../routes/selectors';
import {
  getPastGamesList, getPastGamesPopularity, getPopularityOptions,
  getGameImportState
} from '../gamesSelectors';
import { getUser } from '../../user/userSelectors';

import { UserPropType } from '../../user/types/User';
import { GamePropType } from '../../games/types/Game';

import '../styles/games.scss';

class PastGamesPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
    pastGames: PropTypes.arrayOf(GamePropType).isRequired,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, dispatch } = this.props;
    if (user.pk > 0 && user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  };

  toggleOrientation = () => {
    const { dispatch, popularityOptions } = this.props;
    const { vertical } = popularityOptions;
    dispatch(setPopularityOptions({ vertical: !vertical }));
  };

  render() {
    const { pastGames, popularity, popularityOptions, user } = this.props;

    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <AdminGameActions onDelete={() => true }>
          <PopularityGraph popularity={popularity} options={popularityOptions}
            toggleOrientation={this.toggleOrientation} />
          {user.groups?.guests === true && <div class="alert alert-info" role="alert">
            If you would like to see the track listing of every game, log out from this
            guest account and register an account.</div>}
          <BingoGamesTable games={pastGames} onReload={this.onReload} user={user} past
            title="Previous Bingo games" />
        </AdminGameActions>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    importing: getGameImportState(state),
    location: getLocation(state, ownProps),
    user: getUser(state, ownProps),
    pastGames: getPastGamesList(state, ownProps),
    popularity: getPastGamesPopularity(state, ownProps),
    popularityOptions: getPopularityOptions(state, ownProps),
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
