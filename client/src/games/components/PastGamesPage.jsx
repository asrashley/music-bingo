import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';
import { LoginDialog } from '../../user/components';
import { BingoGamesTable } from './BingoGamesTable';
import '../styles/games.scss';


class PastGamesPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    loggedIn: PropTypes.bool.isRequired,
    user: PropTypes.object,
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
    const { pastGames, loggedIn } = this.props;
    return (
      <div id="games-page" className={loggedIn ? '' : 'modal-open'}  >
        <BingoGamesTable games={pastGames} past title="Previous Bingo games" />
        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  const { games, order, pastOrder } = state.games;
  const { location } = ownProps;
  const pastList = [];
  pastOrder.forEach(pk => pastList.push(games[pk]));
  return {
    loggedIn: userIsLoggedIn(state),
    location,
    user,
    pastGames: pastList,
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
