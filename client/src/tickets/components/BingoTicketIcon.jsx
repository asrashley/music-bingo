import React from 'react';
import PropTypes from 'prop-types';

import { TicketStatus } from '../ticketsSlice';

import { UserPropType } from '../../user/types/User';
import { GamePropType } from '../../games/types/Game';
import { TicketPropTypes } from '../types/Ticket';

export const BingoTicketIcon = ({ game, user, usersMap, ticket, onClick, maxTickets, selected }) => {
  let status;
  const isAdmin = user.groups.admin === true;
  let ticketUser = null;
  if (ticket.user === user.pk) {
    status = TicketStatus.mine;
  } else if (ticket.user === null) {
    if (selected < maxTickets || isAdmin) {
      status = TicketStatus.available;
    } else {
      status = TicketStatus.disabled;
    }
  } else {
    status = TicketStatus.taken;
  }
  let className = `bingo-ticket ${status.enumKey}`;
  if (game.options && game.options.colour_scheme) {
    className += ` ${game.options.colour_scheme}`;
  }

  if (isAdmin && status === TicketStatus.taken && usersMap[ticket.user]) {
    ticketUser = usersMap[ticket.user].username;
  }
  const click = ev => onClick(ticket, ev);
  return (
    <button
      onClick={click}
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
  ticket: TicketPropTypes.isRequired,
  onClick: PropTypes.func.isRequired,
  maxTickets: PropTypes.number.isRequired,
  selected: PropTypes.number.isRequired,
};