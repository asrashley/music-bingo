import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link, Redirect } from 'react-router-dom';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchTicketsIfNeeded, getMyTickets } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicket } from './BingoTicket';

class PlayGamePage extends React.Component {
  componentDidMount() {
    const { dispatch, game } = this.props;
    dispatch(fetchUserIfNeeded())
  }

  componentWillReceiveProps(nextProps) {
    const { dispatch, user, game } = nextProps;
    if (user.pk != this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    } else if (game.pk > 0 && game.pk != this.props.game.pk) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
  }
  render() {
    const { game, tickets, user } = this.props;
    return (
      <div className="card-list">
        {tickets.map((ticket, idx) => <BingoTicket key={idx} ticket={ticket} game={game} user={user}/>)}
      </div>
    );
  }
}

PlayGamePage.propTypes = {
  tickets: PropTypes.array.isRequired,
  game: PropTypes.object.isRequired,
  loggedIn: PropTypes.bool,
};

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  const { gamePk } = ownProps.match.params;
  const tickets = getMyTickets(state, gamePk);
  let game = state.games.games[gamePk];
  if (game === undefined) {
    game = {
      title: '',
      pk: -1,
      tracks: [],
      placeholder: true,
    };
  }

  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game,
    tickets,
  };
};

PlayGamePage = connect(mapStateToProps)(PlayGamePage);

export {
  PlayGamePage
};
