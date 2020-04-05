import React from 'react';

import { TicketStatus } from '../ticketsSlice';

export const BingoTicketIcon = ({ game, user, ticket, addTicket, removeTicket, maxTickets, selected }) => {
  let onClick, status;
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
  if (status === TicketStatus.mine) {
    if (isAdmin) {
      onClick = (ev) => removeTicket(ticket);
    } else {
      onClick = (ev) => false;
    }
  } else if (status === TicketStatus.available) {
    onClick = (ev) => addTicket(ticket);
  } else if (status === TicketStatus.taken && isAdmin) {
    onClick = (ev) => removeTicket(ticket);
  } else {
    onClick = (ev) => false;
  }
  if (isAdmin && status === TicketStatus.taken &&
    user.users[ticket.user]) {
    ticketUser = user.users[ticket.user].username;
  }

  return (
    <button
      onClick={onClick}
      className={`bingo-ticket ${status.enumKey}`}
      data-pk={ticket.pk}
      data-number={ticket.number}>
      <span className="ticket-number">{ticket.number}</span>
      {ticketUser && <div className="owner"><span className="username">{ticketUser}</span></div>}
      {(status === TicketStatus.mine) && <div className="mine"></div>}
    </button>
  );
};
