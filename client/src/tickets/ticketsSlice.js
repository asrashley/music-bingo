import { createSlice } from '@reduxjs/toolkit';
import { Enumify } from 'enumify';

import { api } from '../endpoints';

export class TicketStatus extends Enumify {
  static available = new TicketStatus();
  static mine = new TicketStatus();
  static taken = new TicketStatus();
  static disabled = new TicketStatus();
  static _ = this.closeEnum();
};

export function ticketsInitialState() {
  return ({
    tickets: {},
    order: [],
    tracks: null,
    isFetching: false,
    invalid: true,
    error: null,
    lastUpdated: null,
    updateInterval: 30000,
  });
}

/*
function shuffle(list) {
  let i = list.length;
  if (i == 0) return;
  while (--i) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = list[i];
    list[i] = list[j];
    list[j] = temp;
  }
};
*/

export const ticketsSlice = createSlice({
  name: 'tickets',
  initialState: {
    games: {},
    user: -1,
  },
  reducers: {
    requestTickets: (state, action) => {
      const { gamePk } = action.payload;
      if (state.games[gamePk] === undefined) {
        state.games[gamePk] = ticketsInitialState();
      }
      state.games[gamePk].isFetching = true;
    },
    requestStatusUpdate: (state, action) => {
      const { gamePk } = action.payload;
      if (state.games[gamePk]) {
        state.games[gamePk].isFetching = true;
      }
    },
    receiveTickets: (state, action) => {
      const { payload, timestamp, gamePk, userPk } = action.payload;
      if (state.games[gamePk] === undefined) {
        state.games[gamePk] = ticketsInitialState();
      }
      const game = state.games[gamePk];
      game.order = [];
      game.tickets = {};
      payload.forEach(ticket => {
        game.tickets[ticket.pk] = ticket;
        game.order.push(ticket.pk);
      });
      game.isFetching = false;
      game.error = null;
      game.lastUpdated = timestamp;
      game.invalid = false;
      //TODO: use a middleware to clean out tickets when user logs in
      state.user = userPk;
    },
    failedFetchTickets: (state, action) => {
      const { timestamp, gamePk, error } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      game.tickets.isFetching = false;
      game.tickets.error = error;
      game.tickets.lastUpdated = timestamp;
      game.tickets.invalid = true;
      game.tickets.tickets = [];
    },
    receiveStatusUpdate: (state, action) => {
      const { payload, gamePk, timestamp } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      game.tickets.isFetching = false;
      game.lastUpdated = timestamp;
      const { claimed } = payload;
      for (let pk in claimed) {
        const ticket = game.tickets[pk];
        if (ticket) {
          ticket.user = claimed[pk] ? claimed[pk] : null;
        }
      }
    },
    confirmAddTicket: (state, action) => {
      const { payload } = action.payload;
      const { gamePk, ticketPk, userPk } = payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      const ticket = game.tickets[ticketPk];
      if (ticket && ticket.user === null) {
        ticket.user = userPk;
      }
    },
    confirmRemoveTicket: (state, action) => {
      const { gamePk, ticketPk, userPk } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      const ticket = game.tickets[ticketPk];
      if (ticket && ticket.user === userPk) {
        ticket.user = null;
      }
    }

  },
});

export function addTicket({ gamePk, ticketPk }) {
  return api.claimCard({
    gamePk,
    ticketPk,
    success: ticketsSlice.actions.confirmAddTicket,
  })
    .then(({ payload, user }) => {
      const retval = {
        ...payload,
        success: true,
        userPk: user.pk,
        gamePk,
        ticketPk,
      };
      return retval;
    })
    .catch(error => {
      const result = {
        ...error,
      };
      if (error.status === 404) {
        result.detail = "Unknown ticket";
      } else if (error.status === 406) {
        result.detail = "That ticket has already been taken";
      }
      return result;
    });
}

export function removeTicket({ gamePk, ticketPk, userPk }) {
  return api.releaseCard({
    gamePk,
    ticketPk,
    success: ticketsSlice.actions.confirmRemoveTicket
  });
}

function fetchTickets(userPk, gamePk) {
  return api.getTicketsList({
    gamePk,
    userPk,
    before: ticketsSlice.actions.requestTickets,
    failure: ticketsSlice.actions.failedFetchTickets,
    success: ticketsSlice.actions.receiveTickets,
  });
}
  

function shouldFetchTickets(state, gamePk) {
  const { tickets, user } = state;
  const game = tickets.games[gamePk];
  if (!game) {
    return true;
  }
  if (user.pk !== tickets.user) {
    return true;
  }
  if (game.tickets.isFetching) {
    return false;
  }
  return game.tickets.invalid;
}

export function fetchTicketsIfNeeded(gamePk) {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchTickets(state, gamePk)) {
      return dispatch(fetchTickets(state.user.pk, gamePk));
    }
    const game = state.tickets.games[gamePk];
    return Promise.resolve(game ? game.tickets : null);
  };
}

function fetchStatusUpdate(gamePk) {
  return api.getTicketsStatus({
    gamePk,
    before: ticketsSlice.actions.requestStatusUpdate,
    success: ticketsSlice.actions.receiveStatusUpdate
  });
}


function shouldFetchStatusUpdate(state, gamePk) {
  const { tickets, user } = state;
  const game = tickets.games[gamePk];
  if (!game) {
    return false;
  }
  if (user.pk !== tickets.user) {
    return false;
  }
  if (game.tickets.isFetching || game.tickets.invalid) {
    return false;
  }
  const maxAge = Date.now() - game.updateInterval;
  return (game.lastUpdated === null || game.lastUpdated < maxAge);
}

export function fetchTicketsStatusUpdateIfNeeded(gamePk) {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchStatusUpdate(state, gamePk)) {
      return dispatch(fetchStatusUpdate(gamePk));
    }
  };
}

export const initialState = ticketsSlice.initialState;

export default ticketsSlice.reducer;
