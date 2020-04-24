import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchTicketsIfNeeded, getMyTickets } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicket } from './BingoTicket';

class PlayGamePage extends React.Component {
  static propTypes = {
    tickets: PropTypes.array.isRequired,
    game: PropTypes.object.isRequired,
    loggedIn: PropTypes.bool,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded())
  }

  componentWillReceiveProps(nextProps) {
    const { dispatch, user, game } = nextProps;
    if (user.pk !== this.props.user.pk) {
      dispatch(fetchGamesIfNeeded());
    } else if (game.pk > 0 && game.pk !== this.props.game.pk) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
  }

  render() {
    const { game, tickets, user, loggedIn } = this.props;
    return (
      <div className="card-list">
        {tickets.length===0 && <h2 className="warning">You need to choose a ticket to be able to play!</h2>}
        {tickets.map((ticket, idx) => <BingoTicket key={idx} ticket={ticket} game={game} user={user} />)}
        {!loggedIn && <LoginDialog dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

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
