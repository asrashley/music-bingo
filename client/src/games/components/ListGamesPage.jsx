import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { BingoGamesTable } from './BingoGamesTable';
import { initialState } from '../../app/initialState';

import { getUser } from '../../user/userSelectors';

import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';
import { getActiveGamesList, getPastGamesOrder } from '../gamesSelectors';
import routes from '../../routes';

import '../styles/games.scss';

class ListGamesPage extends React.Component {
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
    const { games, user, pastOrder } = this.props;
    let text = 'If you are feeling nostalgic, why not browe the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    return (
      <div id="games-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <BingoGamesTable games={games} onReload={this.onReload} title="Available Bingo games" />
        {pastOrder.length > 0 && <p>{text}
          <Link to={reverse(`${routes.pastGames}`)} > list of previous Bingo rounds</Link></p>}
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
  };
};

ListGamesPage = connect(mapStateToProps)(ListGamesPage);

export {
  ListGamesPage
};
