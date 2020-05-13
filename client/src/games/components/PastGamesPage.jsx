import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { LoginDialog } from '../../user/components';
import { BingoGamesTable } from './BingoGamesTable';
import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../gamesSlice';
import { getPastGamesList } from '../gamesSelectors';
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

  onReload = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGames());
    dispatch(fetchGamesIfNeeded());
  }

  render() {
    const { pastGames, loggedIn, user } = this.props;
    return (
      <div id="games-page" className={loggedIn ? '' : 'modal-open'}  >
        <BingoGamesTable games={pastGames} onReload={this.onReload} past title="Previous Bingo games" />
        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} user={user}
                                   onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  const { location } = ownProps;
  return {
    loggedIn: userIsLoggedIn(state),
    location,
    user,
    pastGames: getPastGamesList(state),
  };
};

PastGamesPage = connect(mapStateToProps)(PastGamesPage);

export {
  PastGamesPage
};
