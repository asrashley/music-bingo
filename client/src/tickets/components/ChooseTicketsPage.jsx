import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { initialState } from '../../app/initialState';
import routes from '../../routes';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketsStatusUpdateIfNeeded, addTicket, removeTicket } from '../ticketsSlice';
import { getGameTickets, getMyTicketCount } from '../ticketsSelectors';
import { fetchGamesIfNeeded, fetchDetailIfNeeded } from '../../games/gamesSlice';
import { getGamePk, getGame } from '../../games/gamesSelectors';
import { LoginDialog } from '../../user/components/LoginDialog';
import { BingoTicketIcon } from './BingoTicketIcon';
import { AdminDialog } from './AdminDialog';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';
import { FailedSelectionDialog } from './FailedSelectionDialog';
import { TrackListing, ModifyGame } from '../../games/components';

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
  static propTypes = {
    game: PropTypes.object.isRequired,
    tickets: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
    selected: PropTypes.number.isRequired,
    loggedIn: PropTypes.bool,
  };

  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
    };
    this.timer = null;
  }

  componentDidMount() {
    const { dispatch, user, gamePk } = this.props;
    dispatch(fetchUserIfNeeded())
      .then(() => dispatch(fetchGamesIfNeeded()))
      .then(() => dispatch(fetchTicketsIfNeeded(gamePk)))
      .then(() => {
        if (user.groups.admin === true) {
          dispatch(fetchDetailIfNeeded(gamePk));
        }
      });
    this.timer = setInterval(this.pollForTicketChanges, 5000);
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, game, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk ||
      game.pk !== prevProps.game.pk) {
      if (user.groups.admin === true) {
        dispatch(fetchDetailIfNeeded(game.pk));
      }
    }
  }

  componentWillUnmount() {
    this.clearTimer();
  }

  clearTimer = () => {
    if (this.timer !== null) {
      window.clearInterval(this.timer);
      this.timer = null;
    }
  };

  pollForTicketChanges = () => {
    if (this.timer === null) {
      return;
    }
    const { dispatch, gamePk } = this.props;
    if (gamePk > 0) {
      dispatch(fetchTicketsStatusUpdateIfNeeded(gamePk));
    }
  };

  onCancelDialog = () => {
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  onClickTicket = (ticket) => {
    const { history, game, user } = this.props;
    if (user.groups.admin === true) {
      this.showAdminMenu(ticket);
    } else if (ticket.user === null) {
      this.addTicket(ticket);
    } else if (ticket.user === user.pk) {
      history.push(reverse(`${routes.play}`, { gamePk: game.pk }));
    }
    return false;
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

  showAdminMenu = (ticket) => {
    const { game, user } = this.props;
    this.setState({
      ActiveDialog: AdminDialog,
      dialogData: {
        ticket,
        user,
        game,
        onAdd: this.confirmAddTicket,
        onCancel: this.onCancelDialog,
        onRelease: this.confirmRemoveTicket,
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
    const { dispatch, game, tickets, selected, user, loggedIn } = this.props;
    const { ActiveDialog, dialogData } = this.state;
    return (
      <div>
        <div className="ticket-chooser">
          <h1>The theme of this round is "{game.title}"</h1>
          <Instructions game={game} maxTickets={user.options.maxTickets} selected={selected} />
          {tickets.order.map((ticketPk, key) => <BingoTicketIcon
            ticket={tickets.tickets[ticketPk]} key={key}
            onClick={this.onClickTicket}
            game={game}
            user={user}
            maxTickets={user.options.maxTickets}
            selected={selected}
            removeTicket={this.removeTicket}
          />)}
        </div>
        {user.groups.admin === true && <ModifyGame game={game} dispatch={dispatch} />}
        {user.groups.admin === true && <TrackListing game={game} />}

        {loggedIn || <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
        {ActiveDialog && <ActiveDialog {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user } = state;
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    game: getGame(state, ownProps),
    gamePk: getGamePk(state, ownProps),
    tickets: getGameTickets(state, ownProps),
    selected: getMyTicketCount(state, ownProps),
  };
};

ChooseTicketsPage = connect(mapStateToProps)(ChooseTicketsPage);

export {
  ChooseTicketsPage
};
