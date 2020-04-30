import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoGamesTable } from './BingoGamesTable';

import '../styles/games.scss';

class IndexPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    loggedIn: PropTypes.bool.isRequired,
    user: PropTypes.object,
    games: PropTypes.array,
    pastGames: PropTypes.array,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
  }

  componentWillReceiveProps(nextProps) {
    const { user, dispatch } = nextProps;
    if (user.pk !== this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  render() {
    const { games, user, loggedIn } = this.props;
    return (
      <div id="games-page" className={loggedIn ? '' : 'modal-open'}  >
        {user && <h2 className="greeting">Hello {user.username}</h2>}
        <BingoGamesTable games={games} title="Available Bingo games"/>
        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, router } = state;
  const { games, order } = state.games;
  const { location } = router;
  const gameList = [];
  order.forEach(pk => gameList.push(games[pk]));
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    location,
    games: gameList,
  };
};

IndexPage = connect(mapStateToProps)(IndexPage);

export {
  IndexPage
};
