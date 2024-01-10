import { createSelector } from 'reselect';

import { getGame } from '../games/gamesSelectors';
import { ticketInitialState } from './ticketsSlice';
import { getRouteParams } from '../routes/routesSelectors';

const getTicketPk = createSelector([getRouteParams], params => params.ticketPk);

const getTickets = (state) => state.tickets.tickets;
export const getLastUpdated = (state) => state.tickets.lastUpdated;

/* get list of ticket primary keys for the current game */
export const getGameTicketIds = createSelector(
  [getGame], (game) => game.ticketOrder);

const getUser = (state) => state.user;

/* get list of all tickets for a game */
export const getGameTickets = createSelector(
  [getGameTicketIds, getTickets], (order, tickets) => {
    return order.map(pk => tickets[pk]).filter(t => t !== undefined);
  });

function decorateTicket(ticket, game) {
  const { options } = game;
  if (ticket === undefined) {
    ticket = {
      ...ticketInitialState(),
      placeholder: true,
    };
  }
  const rows = [];
  let idx = 0;
  for (let row = 0; row < options.rows && idx < ticket.tracks.length; ++row) {
    const cols = [];
    for (let column = 0; column < options.columns && idx < ticket.tracks.length; ++column) {
      const bit = 1 << idx;
      const checked = (ticket.checked & bit) === bit;
      cols.push({
        ...ticket.tracks[idx],
        background: options ? options.backgrounds[idx] : '',
        checked,
        row,
        column
      });
      idx++;
    }
    rows.push(cols);
  }
  return {
    ...ticket,
    rows
  };
}

export const getTicket = createSelector(
  [getTickets, getTicketPk, getGame],
  (tickets, ticketPk, game) => decorateTicket(tickets[ticketPk], game));

/* get list of tickets for a game owned by the user */
export const getMyGameTickets = createSelector(
  [getGameTicketIds, getTickets, getUser, getGame], (order, tickets, user, game) => {
    return order.map(pk => tickets[pk])
      .filter(ticket => ticket?.user === user.pk)
      .map(ticket => decorateTicket(ticket, game));
  });
