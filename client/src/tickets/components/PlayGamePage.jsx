import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { BingoTicket } from './BingoTicket';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketDetailIfNeeded } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { setChecked } from '../../tickets/ticketsSlice';

/* selectors */
import { getMyGameTickets } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';

/* data */
import { initialState } from '../../app/initialState';

class PlayGamePage extends React.Component {
  static propTypes = {
    tickets: PropTypes.array.isRequired,
    game: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch, game, tickets } = this.props;
    dispatch(fetchUserIfNeeded())
    if (game.pk > 0) {
      dispatch(fetchTicketsIfNeeded(game.pk));
      tickets.forEach(ticket => dispatch(fetchTicketDetailIfNeeded(game.pk, ticket.pk)));
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user, game, tickets } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
    if (game.pk > 0 && game.pk !== prevProps.game.pk) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
    if (game.pk > 0 && tickets.length !== prevProps.tickets.length) {
      tickets.forEach(ticket => dispatch(fetchTicketDetailIfNeeded(game.pk, ticket.pk)));
    }
  }

  setChecked = (values) => {
    const { dispatch } = this.props;
    dispatch(setChecked(values));
  }

  render() {
    const { game, tickets, user } = this.props;
    return (
      <div className="card-list">
        {tickets.length === 0 && <h2 className="warning">You need to choose a ticket to be able to play!</h2>}
        {tickets.map((ticket, idx) => <BingoTicket key={idx} ticket={ticket} game={game}
          setChecked={this.setChecked} download />)}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    game: getGame(state, props),
    tickets: getMyGameTickets(state, props),
  };
};

PlayGamePage = connect(mapStateToProps)(PlayGamePage);

export {
  PlayGamePage
};
