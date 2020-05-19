import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { BingoTicket } from '../cards/components';

import { fetchUserIfNeeded } from '../user/userSlice';
import { fetchGamesIfNeeded, invalidateGames } from '../games/gamesSlice';

import { getActiveGamesList, getPastGamesOrder } from '../games/gamesSelectors';
import { getUser } from '../user/userSelectors';

import { initialState } from './initialState';
import routes from '../routes';

/* import '../styles/games.scss'; */

class IndexPage extends React.Component {
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
      <div id="index-page">
        <BingoTicket/>
        {user && <h2 className="greeting">Hello {user.username}</h2>}
        <h2>Like normal Bingo, but with music!</h2>
        <p>Music Bingo is a variation on normal bingo where the numbers are replaced
          with songs which the players must listen out for.</p>
        {games.length && <p>
                           You can <Link to={reverse(`${routes.listGames}`)}>click here</Link>
                           to see the {games.length} upcoming Bingo games</p>}
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

IndexPage = connect(mapStateToProps)(IndexPage);

export {
  IndexPage
};
