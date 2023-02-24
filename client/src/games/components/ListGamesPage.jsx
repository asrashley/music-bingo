import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { AdminGameActions } from './AdminGameActions';
import { BingoGamesTable } from './BingoGamesTable';
import { DisplayDialogContext } from '../../components/DisplayDialog';

import { getDatabaseImportState } from '../../admin/adminSelectors';
import { getUser } from '../../user/userSelectors';
import {
  getActiveGamesList, getPastGamesOrder, getGameImportState
} from '../gamesSelectors';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';

import { GamePropType } from '../../games/types/Game';
import { UserPropType } from '../../user/types/User';

import '../styles/games.scss';

import routes from '../../routes';

class ListGamesPage extends React.Component {
  static contextType = DisplayDialogContext;

  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
    games: PropTypes.arrayOf(GamePropType),
    pastGames: PropTypes.arrayOf(GamePropType),
    pastOrder: PropTypes.arrayOf(PropTypes.number).isRequired
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
  };

  render() {
    const { games, user, pastOrder } = this.props;

    let text = 'If you are feeling nostalgic, why not browse the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <AdminGameActions>
          <BingoGamesTable
            games={games}
            onReload={this.onReload}
            user={user}
            title="Available Bingo games"
          />
          {pastOrder.length > 0 && <p>{text}
            <Link to={reverse(`${routes.pastGames}`)} > list of previous Bingo rounds</Link></p>}
        </AdminGameActions>
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
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
