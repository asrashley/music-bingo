import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { initialState } from '../../app/initialState';
import routes from '../../routes';
import { fetchUserIfNeeded, userIsLoggedIn, setActiveGame } from '../../user/userSlice';
import { fetchTicketsIfNeeded, ticketsInitialState, addTicket, removeTicket, TicketStatus } from '../ticketsSlice';
import { fetchGamesIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { ModalDialog } from '../../components';

import '../styles/tickets.scss';

const BingoTicketIcon = ({ game, user, ticket, addTicket, removeTicket, maxTickets, selected }) => {
  let onClick, status;

  if (ticket.user === user.pk) {
    status = TicketStatus.mine;
  } else if (ticket.user === null) {
    if (selected < maxTickets) {
      status = TicketStatus.available;
    } else {
      status = TicketStatus.disabled;
    }
  } else {
    status = TicketStatus.taken;
  }
  if (status === TicketStatus.mine) {
    onClick = (ev) => removeTicket(user.pk, game.pk, ticket.pk);
  } else if (status === TicketStatus.available) {
    onClick = (ev) => addTicket(user.pk, game.pk, ticket.pk);
  } else {
    onClick = (ev) => false;
  }
  return (
    <button
      onClick={onClick}
      className={`bingo-ticket ${status.enumKey}`}
      data-pk={ticket.pk}
      data-number={ticket.number}>
      <span className="ticket-number">{ticket.number}</span>
      {(status === TicketStatus.mine) && <div className="mine"></div>}
    </button>
  );
};

class ConfirmSelectionDialog extends React.Component {
  static propTypes = {
    ticket: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired,
    onConfirm: PropTypes.func.isRequired,
  };

  render() {
    const { ticket, onCancel, onConfirm } = this.props;
    const footer = (
      <div>
        <button className="btn btn-primary yes-button"
          onClick={() => onConfirm(ticket)} > Yes</button>
        <button className="btn btn-secondary cancel-button"
          data-dismiss="modal" onClick={onCancel}>Cancel</button>
      </div>
    );
    return (
      <ModalDialog
        className="confirm-select-ticket"
        id="confirm-select"
        onCancel={onCancel}
        title="Confirm ticket choice"
        footer={footer}
      >
        <h3>Would you like to choose ticket {ticket.number}?</h3>
        <p className="warning">Once you click yes, there is no way back and
          you cannot undo your selection!</p>
      </ModalDialog>
    );
  }
}

class ManageGamePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
    };
  }

  componentDidMount() {
    const { dispatch, gamePk } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()))
      .then(() => dispatch(fetchTicketsIfNeeded(gamePk)))
      .then(() => dispatch(setActiveGame(gamePk)));
  }

  onCancelDialog = () => {
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  onConfirmTicket = (ticket) => {
    const { game, dispatch, user } = this.props;
    dispatch(addTicket({
      userPk: user.pk,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }));
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  addTicket = (userPk, gamePk, ticketPk) => {
    const { tickets } = this.props;
    const ticket = tickets.tickets[ticketPk];
    if (!ticket) {
      return;
    }
    this.setState({
      ActiveDialog: ConfirmSelectionDialog,
      dialogData: {
        ticket,
        onCancel: this.onCancelDialog,
        onConfirm: this.onConfirmTicket,
      }
    });
  };

  removeTicket = (userPk, gamePk, ticketPk) => {
    const { dispatch } = this.props;
    dispatch(removeTicket({ userPk, gamePk, ticketPk }));
  };


  render() {
    const { game, tickets, selected, user, loggedIn } = this.props;
    const { ActiveDialog, dialogData } = this.state;
    return (
      <div className="ticket-chooser ticket-manager">
        <h1>The theme of this round is "{game.title}"</h1>
        {tickets.order.map((ticketPk, key) => <BingoTicketIcon
          ticket={tickets.tickets[ticketPk]} key={key}
          addTicket={this.addTicket}
          game={game}
          user={user}
          maxTickets={user.options.maxTickets}
          selected={selected}
          removeTicket={this.removeTicket}
        />)}
        {loggedIn || < LoginDialog {...this.props} />}
        {ActiveDialog && <ActiveDialog {...dialogData} />}
      </div>
    );
  }
}

ManageGamePage.propTypes = {
  game: PropTypes.object.isRequired,
  tickets: PropTypes.object.isRequired,
  selected: PropTypes.number.isRequired,
  loggedIn: PropTypes.bool,
};

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  //console.dir(ownProps);
  const { user } = state;
  const { gamePk } = ownProps.match.params;
  let game = state.games.games[gamePk];
  if (game === undefined) {
    game = {
      title: '',
      pk: -1,
    };
  }
  let tickets;
  if (state.tickets.games[gamePk]) {
    tickets = state.tickets.games[gamePk];
  } else {
    tickets = ticketsInitialState();
  }
  let selected = 0;
  Object.keys(tickets.tickets).forEach(pk => {
    /*if (pk === null) {
        return;
    }
    console.log(`pk ${pk}`);
    order.push(pk);*/
    if (tickets.tickets[pk].user === user.pk) {
      selected++;
    }
  });
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game,
    gamePk,
    tickets,
    selected,
  };
};

ManageGamePage = connect(mapStateToProps)(ManageGamePage);

export {
  ManageGamePage
};
