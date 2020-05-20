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
import { getTicket } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';

/* data */
import { initialState } from '../../app/initialState';

class ViewTicketPage extends React.Component {
  static propTypes = {
    ticket: PropTypes.object.isRequired,
    game: PropTypes.object.isRequired,
    loggedIn: PropTypes.bool,
  };

  componentDidMount() {
    const { dispatch, game, ticket, user } = this.props;
    dispatch(fetchUserIfNeeded());
    if (!user.loggedIn) {
      return;
    }
    dispatch(fetchGamesIfNeeded());
    if (game.pk <= 0) {
      return;
    }
    dispatch(fetchTicketsIfNeeded(game.pk));
    if (ticket.pk > 0) {
      dispatch(fetchTicketDetailIfNeeded(game.pk, ticket.pk));
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user, game, ticket } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    }
    if (game.pk > 0 && game.pk !== prevProps.game.pk) {
      dispatch(fetchTicketsIfNeeded(game.pk));
    }
    if (game.pk > 0 && ticket.pk > 0 && ticket.pk !== prevProps.ticket.pk) {
      dispatch(fetchTicketDetailIfNeeded(game.pk, ticket.pk));
    }
  }

  setChecked = (values) => {
    const { dispatch } = this.props;
    dispatch(setChecked(values));
  }

  render() {
    const { dispatch, game, ticket } = this.props;
    return (
      <div className="card-list">
        <BingoTicket ticket={ticket} game={game} setChecked={this.setChecked}
          dispatch={dispatch} download />
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    game: getGame(state, props),
    ticket: getTicket(state, props),
  };
};

ViewTicketPage = connect(mapStateToProps)(ViewTicketPage);

export {
  ViewTicketPage
};
