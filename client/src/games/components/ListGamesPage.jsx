import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { AdminActionPanel, AdminGameActions} from './AdminGameActions';
import { BingoGamesTable } from './BingoGamesTable';

import { getDatabaseImportState } from '../../admin/adminSelectors';
import { getUser } from '../../user/userSelectors';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import {
  getActiveGamesList, getPastGamesOrder, getGameImportState
} from '../gamesSelectors';

import '../styles/games.scss';

import routes from '../../routes';
import { initialState } from '../../app/initialState';

class ListGamesPage extends AdminGameActions {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: PropTypes.object.isRequired,
    games: PropTypes.array,
    pastGames: PropTypes.array,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()));
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  }

  render() {
    const { games, user, pastOrder, databaseImporting, gameImporting } = this.props;
    const { ActiveDialog, dialogData, importType } = this.state;
    let importing = {};
    if (importType === AdminGameActions.DATABASE_IMPORT) {
      importing = databaseImporting;
    } else if (importType === AdminGameActions.GAME_IMPORT) {
      importing = gameImporting;
    }

    let text = 'If you are feeling nostalgic, why not browse the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        {(user.groups.admin === true) && <AdminActionPanel importGame={this.onClickImportGame} />}
        <BingoGamesTable
          games={games}
          onReload={this.onReload}
          user={user}
          title="Available Bingo games"
        />
        {pastOrder.length > 0 && <p>{text}
          <Link to={reverse(`${routes.pastGames}`)} > list of previous Bingo rounds</Link></p>}
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} {...importing} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    games: getActiveGamesList(state),
    pastOrder: getPastGamesOrder(state),
    databaseImporting: getDatabaseImportState(state),
    gameImporting: getGameImportState(state),
  };
};

ListGamesPage = connect(mapStateToProps)(ListGamesPage);

export {
  ListGamesPage
};
