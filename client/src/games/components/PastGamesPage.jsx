import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoGamesTable } from './BingoGamesTable';
import { AdminActions } from '../../admin/components/AdminActions';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { getPastGamesList } from '../gamesSelectors';
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

  render() {
    const { pastGames, user } = this.props;

    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}>
        <AdminActions alwaysShowChildren={true}>
          <button className="btn btn-primary"
            onClick={this.onReload}>Reload</button>
        </AdminActions>
        {user.groups?.guests === true && <div class="alert alert-info" role="alert">
          If you would like to see the track listing of every game, log out from this
          guest account and register an account.</div>}
        <BingoGamesTable games={pastGames} onReload={this.onReload} user={user} past
          title="Previous Bingo games" />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    user: getUser(state, ownProps),
    pastGames: getPastGamesList(state, ownProps),
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
