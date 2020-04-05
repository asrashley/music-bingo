import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { initialState } from '../../app/initialState';
import routes from '../../routes';
import { fetchUserIfNeeded, userIsLoggedIn, setActiveGame } from '../../user/userSlice';
import { fetchTicketsIfNeeded, ticketsInitialState, addTicket, removeTicket, TicketStatus } from '../ticketsSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded } from '../../games/gamesSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { ModalDialog } from '../../components';
import { BingoTicketIcon } from './BingoTicketIcon';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';
import { FailedSelectionDialog } from './FailedSelectionDialog';
import { TrackListing } from './TrackListing';

import '../styles/tickets.scss';

const Instructions = ({ game, selected, maxTickets }) => {
  if (selected === 0) {
    return (<p className="instructions">Please select a Bingo Ticket</p>);
  }
  const link = <Link to={reverse(`${routes.play}`, { gamePk: game.pk })}
    className="btn btn-primary play-game">Let's play!</Link>;
  let text;
  if (selected === 1) {
    text = "You have selected a ticket";
  } else if (selected === maxTickets) {
    text = `You have selected ${selected} tickets and cannot select any additional tickets`;
  } else {
    text = `You have selected ${selected} tickets`;
  }
  return (
    <p className="instructions">{text}{link}</p>
  );
};

class ChooseTicketsPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
    };
  }

  componentDidMount() {
    const { dispatch, user, gamePk } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()))
      .then(() => dispatch(fetchTicketsIfNeeded(gamePk)))
      .then(() => dispatch(setActiveGame(gamePk))).
      then(() => {
        if (user.groups.admin === true) {
          dispatch(fetchDetailIfNeeded(gamePk));
        }
      });

  }

  componentWillReceiveProps(nextProps) {
    const { user, game, dispatch } = nextProps;
    if (user.pk != this.props.user.pk ||
      game.pk != this.props.game.pk) {
      if (user.groups.admin === true) {
        dispatch(fetchDetailIfNeeded(game.pk));
      }
    }
  }

  onCancelDialog = () => {
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  addTicket = (ticket) => {
    this.setState({
      ActiveDialog: ConfirmSelectionDialog,
      dialogData: {
        ticket,
        onCancel: this.onCancelDialog,
        onConfirm: this.confirmAddTicket,
      }
    });
  };

  confirmAddTicket = (ticket) => {
    const { game, dispatch, user } = this.props;
    dispatch(addTicket({
      userPk: user.pk,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }))
      .then(result => {
        if (result.success !== true) {
          this.setState({
            ActiveDialog: FailedSelectionDialog,
            dialogData: {
              ticket,
              onCancel: this.onCancelDialog,
            },
          });
        }
      });
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  removeTicket = (ticket) => {
    const { user } = this.props;
    this.setState({
      ActiveDialog: ConfirmSelectionDialog,
      dialogData: {
        ticket,
        user,
        onCancel: this.onCancelDialog,
        onConfirm: this.confirmRemoveTicket,
      }
    });
  };

  confirmRemoveTicket = (ticket) => {
    const { game, dispatch } = this.props;
    dispatch(removeTicket({
      userPk: ticket.user,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }));
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };


  render() {
    const { game, tickets, selected, user, loggedIn } = this.props;
    const { ActiveDialog, dialogData } = this.state;
    return (
      <div className="content">
        <div className="ticket-chooser">
          <h1>The theme of this round is "{game.title}"</h1>
          <Instructions game={game} maxTickets={user.options.maxTickets} selected={selected} />
          {tickets.order.map((ticketPk, key) => <BingoTicketIcon
            ticket={tickets.tickets[ticketPk]} key={key}
            addTicket={this.addTicket}
            game={game}
            user={user}
            maxTickets={user.options.maxTickets}
            selected={selected}
            removeTicket={this.removeTicket}
          />)}
        </div>
        {user.groups.admin === true && <TrackListing game={game} />}
        {loggedIn || < LoginDialog {...this.props} />}
        {ActiveDialog && <ActiveDialog {...dialogData} />}
      </div>
    );
  }
}

ChooseTicketsPage.propTypes = {
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
      tracks: [],
      placeholder: true,
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

ChooseTicketsPage = connect(mapStateToProps)(ChooseTicketsPage);

export {
  ChooseTicketsPage
};
