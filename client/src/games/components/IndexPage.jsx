import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoGamesTable } from './BingoGamesTable';
import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchGamesIfNeeded } from '../gamesSlice';
import { getActiveGamesList, getPastGamesOrder } from '../gamesSelectors';
import routes from '../../routes';

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
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()));
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
  }

  render() {
    const { games, user, loggedIn, pastOrder } = this.props;
    let text = 'If you are feeling nostalgic, why not browe the ';
    if (games.length === 0) {
      text = 'There are no upcoming Bingo games, but in the meantime you could browse the';
    }
    return (
      <div id="games-page" className={loggedIn ? '' : 'modal-open'}  >
        {user && <h2 className="greeting">Hello {user.username}</h2>}
        <BingoGamesTable games={games} title="Available Bingo games" />
        {pastOrder.length > 0 && <p>{text}
          <Link to={reverse(`${routes.pastGames}`)} > list of previous Bingo rounds</Link></p>}
        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, router } = state;
  const { location } = router;
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    location,
    games: getActiveGamesList(state),
    pastOrder: getPastGamesOrder(state),
  };
};

IndexPage = connect(mapStateToProps)(IndexPage);

export {
  IndexPage
};
