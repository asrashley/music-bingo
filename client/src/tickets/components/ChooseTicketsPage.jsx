import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import log from 'loglevel';

/* components */
import { DisplayDialogContext } from '../../components/DisplayDialog';
import { BingoTicketIcon } from './BingoTicketIcon';
import { AdminTicketDialog } from './AdminTicketDialog';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';
import { FailedSelectionDialog } from './FailedSelectionDialog';
import { TrackListing, ModifyGame } from '../../games/components';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchTicketsIfNeeded, fetchTicketsStatusUpdateIfNeeded, claimTicket, releaseTicket } from '../ticketsSlice';
import { fetchGamesIfNeeded, fetchDetailIfNeeded, invalidateGameDetail } from '../../games/gamesSlice';
import { fetchUsersIfNeeded } from '../../admin/adminSlice';

/* selectors */
import { getMyGameTickets, getGameTickets, getLastUpdated } from '../ticketsSelectors';
import { getGame } from '../../games/gamesSelectors';
import { getUser } from '../../user/userSelectors';
import { getUsersMap } from '../../admin/adminSelectors';

/* data */
import routes from '../../routes';

/* prop types */
import { GamePropType } from '../../games/types/Game';
import { UserPropType } from '../../user/types/User';
import { TicketPropType } from '../types/Ticket';

import '../styles/tickets.scss';

function Instructions({ game, selected, maxTickets }) {
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
Instructions.propTypes = {
  game: GamePropType.isRequired,
  selected: PropTypes.number.isRequired,
  maxTickets: PropTypes.number.isRequired
};

class ChooseTicketsPage extends React.Component {
  static ticketPollInterval = 5000;
  static contextType = DisplayDialogContext;
  static propTypes = {
    game: GamePropType.isRequired,
    history: PropTypes.object.isRequired,
    tickets: PropTypes.arrayOf(TicketPropType).isRequired,
    user: UserPropType.isRequired,
    usersMap: PropTypes.object,
    myTickets: PropTypes.array.isRequired,
    lastUpdated: PropTypes.number.isRequired,
    loggedIn: PropTypes.bool,
  };

  constructor(props) {
    super(props);
    this.timer = null;
  }

  componentDidMount() {
    const { dispatch, user, game } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchGamesIfNeeded());
    if (game.pk > 0) {
      dispatch(fetchTicketsIfNeeded(game.pk));
      if (user.groups.admin === true || user.groups.hosts === true) {
        dispatch(fetchDetailIfNeeded(game.pk));
        dispatch(fetchUsersIfNeeded());
      }
    }
    this.timer = setInterval(this.pollForTicketChanges, ChooseTicketsPage.ticketPollInterval);
  }

  componentDidUpdate(prevProps, prevState) {
    const { user, game, dispatch } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchGamesIfNeeded());
    } else if (game.pk !== prevProps.game.pk) {
      if (game.pk > 0) {
        dispatch(fetchTicketsIfNeeded(game.pk));
        if (user.groups.admin === true || user.groups.hosts === true) {
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
    const { closeDialog } = this.context;
    closeDialog();
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
    const { user } = this.props;
    const { openDialog } = this.context;
    openDialog(<ConfirmSelectionDialog
      ticket={ticket}
      user={user}
      onCancel={this.onCancelDialog}
      onConfirm={this.confirmAddTicket}
    />);
  };

  confirmAddTicket = (ticket) => {
    const { game, dispatch, user } = this.props;
    const { closeDialog, openDialog } = this.context;
    closeDialog();
    dispatch(claimTicket({
      userPk: user.pk,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }))
      .then(response => {
        const { payload } = response;
        if (payload.status === 406) {
          openDialog(<FailedSelectionDialog
            ticket={ticket}
            onCancel={this.onCancelDialog}
          />);
        }
      });
  };

  showAdminMenu = (ticket) => {
    const { game, user, usersMap } = this.props;
    const { openDialog } = this.context;
    openDialog(<AdminTicketDialog
      ticket={ticket}
      user={user}
      usersMap={usersMap}
      game={game}
      onAdd={this.confirmAddTicket}
      onCancel={this.onCancelDialog}
      onRelease={this.confirmRemoveTicket}
    />);
  };

  confirmRemoveTicket = (ticket) => {
    const { game, dispatch } = this.props;
    const { closeDialog } = this.context;
    closeDialog();
    dispatch(releaseTicket({
      userPk: ticket.user,
      gamePk: game.pk,
      ticketPk: ticket.pk,
    }));
  };

  onGameDelete = () => {
    const { history } = this.props;
    history.push(`${routes.index}`);
  }

  reload = () => {
    const { game, dispatch, user } = this.props;
    log.debug('reload game and tickets');
    dispatch(invalidateGameDetail({ game }));
    dispatch(fetchTicketsIfNeeded(game.pk));
    if (user.groups.admin === true) {
      log.debug('User is admin - fetch details and users');
      dispatch(fetchDetailIfNeeded(game.pk));
      dispatch(fetchUsersIfNeeded());
    }
  }

  render() {
    const { dispatch, game, lastUpdated, tickets, myTickets, user, usersMap } = this.props;
    const selected = myTickets.length;
    return (
      <div>
        <div
          className="ticket-chooser"
          data-last-update={lastUpdated}
          data-game-last-update={game.lastUpdated} >
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
          onReload={this.reload} />}
        {user.groups.admin === true && <TrackListing game={game} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    user: getUser(state, ownProps),
    usersMap: getUsersMap(state, ownProps),
    game: getGame(state, ownProps),
    tickets: getGameTickets(state, ownProps),
    myTickets: getMyGameTickets(state, ownProps),
    lastUpdated: getLastUpdated(state, ownProps),
  };
};

ChooseTicketsPage = connect(mapStateToProps)(ChooseTicketsPage);

export {
  ChooseTicketsPage
};
