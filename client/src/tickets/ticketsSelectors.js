import { createSelector } from 'reselect';

import { ticketsInitialState } from './ticketsSlice';

export const getGamePk = (state, props) => {
  return props.match.params.gamePk;
};

const getTicketPk = (state, props) => {
  return props.match.params.ticketPk;
};

const getGames = (state, props) => state.tickets.games;

export const getGameTickets = createSelector(
  [getGamePk, getGames], (gamePk, games) => {
    if (games[gamePk] === undefined) {
      return ticketsInitialState();
    }
    return games[gamePk];
  });

const getUser = (state) => state.user;

export const makeGetMyTickets = () => createSelector(
  [getGameTickets, getUser], (game, user) => {
    if (!game) {
      return [];
    }
    const retval = [];
    Object.keys(game.tickets).forEach(pk => {
      const ticket = game.tickets[pk];
      if (ticket.user === user.pk) {
        retval.push(ticket);
      }
    });
    return retval;
});

export const getTicket = createSelector(
  [getGameTickets, getTicketPk],
  (game, ticketPk) => {
    if (game.tickets[ticketPk] === undefined) {
      return {
        title: '',
        pk: -1,
        tracks: [],
        placeholder: true,
      };
    }
    return game.tickets[ticketPk];
    /*Object.keys(game.tickets).forEach(pk => {
      const ticket = game.tickets[pk];
      if (ticket.pk === ticketPk) {
        return ticket;
      }
    });
    return null;*/
  });

export const getMyTicketCount = createSelector(
  [getGameTickets, getUser], (game, user) => {
  if (!game) {
    return [];
  }
  let count = 0;
  Object.keys(game.tickets).forEach(pk => {
    const ticket = game.tickets[pk];
    if (ticket.user === user.pk) {
      count++;
    }
  });
  return count;
});
