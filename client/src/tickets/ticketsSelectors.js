import { createSelector } from 'reselect';

import { getGame } from '../games/gamesSelectors';
import { ticketInitialState } from './ticketsSlice';

/*
export const getGameId = (state, props) => props.match.params.gameId;
const getIdMap = (state) => state.games.gameIds;

const getGamePk = createSelector(
  [getGameId, getIdMap], (gameId, idMap) => idMap[gameId]);
*/

const getTicketPk = (state, props) => props.match.params.ticketPk;

/*const getGames = (state, props) => state.tickets.games;*/

const getTickets = (state, props) => state.tickets.tickets;

/* get list of ticket primary keys for the current game */
export const getGameTicketIds = createSelector(
  [getGame], (game) => game.ticketOrder);

const getUser = (state) => state.user;

/* get list of all tickets for a game */
export const getGameTickets = createSelector(
  [getGameTicketIds, getTickets], (order, tickets) => {
    return order.map(pk => tickets[pk]).filter(t => t !== undefined);
  });

/* get list of tickets for a game owned by the user */
export const getMyGameTickets = createSelector(
  [getGameTicketIds, getTickets, getUser], (order, tickets, user) => {
    return order.map(pk => tickets[pk]).filter(t => t && t.user === user.pk);
  });


export const getTicket = createSelector(
  [getTickets, getTicketPk],
  (tickets, ticketPk) => {
    if (tickets[ticketPk] === undefined) {
      return {
        ...ticketInitialState(),
        placeholder: true,
      };
    }
    return tickets[ticketPk];
  });
