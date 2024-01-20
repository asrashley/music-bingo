import React, { useCallback, useContext, useMemo } from 'react';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import { push } from '@lagunovsky/redux-react-router';
import { reverse } from 'named-urls';
import log from 'loglevel';

import { DisplayDialogContext } from '../../components/DisplayDialog';
import { AdminTicketDialog } from './AdminTicketDialog';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';
import { FailedSelectionDialog } from './FailedSelectionDialog';

import { TicketStatus, claimTicket, releaseTicket } from '../ticketsSlice';

import { UserPropType } from '../../user/types/User';
import { GamePropType } from '../../games/types/Game';
import { TicketPropType } from '../types/Ticket';
import { routes } from '../../routes/routes';

export const BingoTicketIcon = ({ game, user, usersMap, ticket, maxTickets, selected }) => {
  const dispatch = useDispatch();
  const { openDialog, closeDialog } = useContext(DisplayDialogContext);

  const isAdmin = user.groups.admin === true;
  const status = useMemo(() => {
    if (ticket.user === user.pk) {
      return TicketStatus.mine;
    }
    if (ticket.user === null) {
      if (selected < maxTickets || isAdmin) {
        return TicketStatus.available;
      } else {
        return TicketStatus.disabled;
      }
    }
    return TicketStatus.taken;
  }, [ticket.user, user.pk, selected, maxTickets, isAdmin]);

  let className = `bingo-ticket ${status.enumKey}`;
  if (game.options && game.options.colour_scheme) {
    className += ` ${game.options.colour_scheme}`;
  }

  let ticketUser = null;
  if (isAdmin && status === TicketStatus.taken && usersMap[ticket.user]) {
    ticketUser = usersMap[ticket.user].username;
  }

  const onClick = useCallback(() => {
    const confirmRemoveTicket = (ticket) => {
      closeDialog();
      dispatch(releaseTicket({
        userPk: ticket.user,
        gamePk: game.pk,
        ticketPk: ticket.pk,
      }));
    };

    const confirmAddTicket = async (ticket) => {
      closeDialog();
      const { payload } = await dispatch(claimTicket({
        userPk: user.pk,
        gamePk: game.pk,
        ticketPk: ticket.pk,
      }));
      if (payload?.status === 406) {
        openDialog(<FailedSelectionDialog
          ticket={ticket}
          onCancel={closeDialog}
        />);
      }
    };

    const viewTicket = () => {
      closeDialog();
      const url = reverse(`${routes.viewTicket}`, { gameId: game.id, ticketPk: ticket.pk });
      dispatch(push(url));
    };

    const showAdminMenu = (ticket) => {
      openDialog(<AdminTicketDialog
        ticket={ticket}
        user={user}
        usersMap={usersMap}
        game={game}
        onAdd={confirmAddTicket}
        onCancel={closeDialog}
        onRelease={confirmRemoveTicket}
        onView={viewTicket}
      />);
    };

    const addTicket = (ticket) => {
      openDialog(<ConfirmSelectionDialog
        ticket={ticket}
        user={user}
        onCancel={closeDialog}
        onConfirm={confirmAddTicket}
      />);
    };

    if (user.groups.admin === true) {
      showAdminMenu(ticket);
    } else if (ticket.user === null) {
      addTicket(ticket);
    } else if (ticket.user === user.pk) {
      dispatch(push(reverse(`${routes.play}`, { gameId: game.id })));
    } else {
      log.debug('BingoTicketIcon.onClick: nothing to do', ticket.user, user.pk);
    }
  }, [closeDialog, dispatch, game, openDialog, ticket, user, usersMap]);

  /*
  const removeTicket = (ticket) => {
    openDialog(<ConfirmSelectionDialog
      ticket={ticket}
      user={user}
      onCancel={closeDialog}
      onConfirm={confirmRemoveTicket}
    />);
  };

 */

  return (
    <button
      onClick={onClick}
      className={className}
      data-pk={ticket.pk}
      data-number={ticket.number}>
      <span className="ticket-number">{ticket.number}</span>
      {ticketUser && <div className="owner"><span className="username">{ticketUser}</span></div>}
      {(status === TicketStatus.mine) && <div className="mine"></div>}
    </button>
  );
};

BingoTicketIcon.propTypes = {
  game: GamePropType.isRequired,
  user: UserPropType.isRequired,
  usersMap: PropTypes.object,
  ticket: TicketPropType.isRequired,
  maxTickets: PropTypes.number.isRequired,
  selected: PropTypes.number.isRequired,
};