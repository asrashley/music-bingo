import React from 'react';
import PropTypes from 'prop-types';

import { TicketStatus } from '../ticketsSlice';

export const BingoTicketIcon = ({ user, ticket, onClick, maxTickets, selected }) => {
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

  if (isAdmin && status === TicketStatus.taken &&
    user.users[ticket.user]) {
    ticketUser = user.users[ticket.user].username;
  }
  const click = ev => onClick(ticket, ev);
  return (
    <button
      onClick={click}
      className={`bingo-ticket ${status.enumKey}`}
      data-pk={ticket.pk}
      data-number={ticket.number}>
      <span className="ticket-number">{ticket.number}</span>
      {ticketUser && <div className="owner"><span className="username">{ticketUser}</span></div>}
      {(status === TicketStatus.mine) && <div className="mine"></div>}
    </button>
  );
};

BingoTicketIcon.propTypes = {
  user: PropTypes.object.isRequired,
  ticket: PropTypes.object.isRequired,
  onClick: PropTypes.func.isRequired,
  maxTickets: PropTypes.number.isRequired,
  selected: PropTypes.number.isRequired,
};