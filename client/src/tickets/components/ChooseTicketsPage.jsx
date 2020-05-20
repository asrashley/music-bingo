import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

/* components */
import { BingoTicketIcon } from './BingoTicketIcon';
import { AdminDialog } from './AdminDialog';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';
import { FailedSelectionDialog } from './FailedSelectionDialog';
import { TrackListing, ModifyGame } from '../../games/components';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketsStatusUpdateIfNeeded, claimTicket, releaseTicket } from '../ticketsSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded, invalidateGameDetail } from '../../games/gamesSlice';
import { fetchUsersIfNeeded } from '../../admin/adminSlice';

/* selectors */
import { getMyGameTickets, getGameTickets } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';
import { getUsersMap } from '../../admin/adminSelectors';

/* data */
import { initialState } from '../../app/initialState';
import routes from '../../routes';

import '../styles/tickets.scss';

const Instructions = ({ game, selected, maxTickets }) => {
  if (selected === 0) {
    return (<p className="instructions">Please select a Bingo Ticket</p>);
  }
  const link = <Link to={reverse(`${routes.play}`, { gameId: game.id })}
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
    tickets: PropTypes.array.isRequired,
    user: PropTypes.object.isRequired,
    usersMap: PropTypes.object,
    myTickets: PropTypes.array.isRequired,
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
    const { dispatch, user, game } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
    if (game.pk > 0) {
      dispatch(fetchTicketsIfNeeded(game.pk));
      if (user.groups.admin === true || user.groups.host === true) {
        dispatch(fetchDetailIfNeeded(game.pk));
        dispatch(fetchUsersIfNeeded());
      }
    }
    this.timer = setInterval(this.pollForTicketChanges, 5000);
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, game, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    } else if (game.pk !== prevProps.game.pk) {
      if (game.pk > 0) {
        dispatch(fetchTicketsIfNeeded(game.pk));
        if (user.groups.admin === true || user.groups.host === true) {
          dispatch(fetchDetailIfNeeded(game.pk));
          dispatch(fetchUsersIfNeeded());
        }
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
    const { dispatch, game } = this.props;
    if (game.pk > 0) {
      dispatch(fetchTicketsStatusUpdateIfNeeded(game.pk));
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
      history.push(reverse(`${routes.play}`, { gameId: game.id }));
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
    dispatch(claimTicket({
      userPk: user.pk,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }))
      .then(response => {
        const { payload } = response;
        if (payload.status === 406) {
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
    const { game, user, usersMap } = this.props;
    this.setState({
      ActiveDialog: AdminDialog,
      dialogData: {
        ticket,
        user,
        usersMap,
        game,
        onAdd: this.confirmAddTicket,
        onCancel: this.onCancelDialog,
        onRelease: this.confirmRemoveTicket,
      }
    });
  };

  confirmRemoveTicket = (ticket) => {
    const { game, dispatch } = this.props;
    dispatch(releaseTicket({
      userPk: ticket.user,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }));
    this.setState({
      ActiveDialog: null,
      dialogData: null,
    });
  };

  onGameDelete = () => {
    const { history } = this.props;
    history.push(`${routes.index}`);
  }

  reload = () => {
    const { game, dispatch, user } = this.props;
    dispatch(invalidateGameDetail(game.pk));
    dispatch(fetchTicketsIfNeeded(game.pk));
    if (user.groups.admin === true) {
      dispatch(fetchDetailIfNeeded(game.pk));
      dispatch(fetchUsersIfNeeded());
    }
  }


  render() {
    const { dispatch, game, tickets, myTickets, user, usersMap } = this.props;
    const { ActiveDialog, dialogData } = this.state;
    const selected = myTickets.length;
    return (
      <div>
        <div className="ticket-chooser">
          <h1>The theme of this round is "{game.title}"</h1>
          <Instructions game={game} maxTickets={user.options.maxTickets} selected={selected} />
          {tickets.map((ticket, key) => <BingoTicketIcon
            ticket={ticket} key={key}
            onClick={this.onClickTicket}
            game={game}
            user={user}
            usersMap={usersMap}
            maxTickets={user.options.maxTickets}
            selected={selected}
            removeTicket={this.removeTicket}
          />)}
        </div>
        {user.groups.admin === true && <ModifyGame game={game} dispatch={dispatch}
          onDelete={this.onGameDelete} options={user.options}
          onReload={this.reload }/>}
        {user.groups.admin === true && <TrackListing game={game} />}
        {ActiveDialog && <ActiveDialog {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    user: getUser(state, ownProps),
    usersMap: getUsersMap(state, ownProps),
    game: getGame(state, ownProps),
    tickets: getGameTickets(state, ownProps),
    myTickets: getMyGameTickets(state, ownProps),
  };
};

ChooseTicketsPage = connect(mapStateToProps)(ChooseTicketsPage);

export {
  ChooseTicketsPage
};
