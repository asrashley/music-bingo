import { createSlice } from '@reduxjs/toolkit';
import { Enumify } from 'enumify';
import log from 'loglevel';

import { receiveGameTickets } from '../games/gamesSlice';
import { userChangeListeners } from '../user/userSlice';
import { api } from '../endpoints';

export class TicketStatus extends Enumify {
  static available = new TicketStatus();
  static mine = new TicketStatus();
  static taken = new TicketStatus();
  static disabled = new TicketStatus();
  static _ = this.closeEnum();
}

export function gameInitialState() {
  return ({
    tracks: null,
    isFetching: false,
    invalid: true,
    error: null,
    lastUpdated: 0,
  });
}

export function ticketInitialState() {
  return ({
    pk: -1,
    number: -1,
    game: -1,
    title: '',
    tracks: [],
    checked: 0,
    user: null,
    lastUpdated: 0,
  });
}

export const initialState = {
  games: {},
  tickets: {},
  user: -1,
  isFetching: false,
  lastUpdated: 0,
  updateInterval: 30000
};

export const ticketsSlice = createSlice({
  name: 'tickets',
  initialState,
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.user && state.isFetching !== true) {
        state.games = {};
        state.tickets = {};
        state.user = user.pk;
        state.lastUpdated = Date.now();
      }
    },
    logoutUser: (state) => {
      state.games = {};
      state.tickets = {};
      state.user = -1;
      state.lastUpdated = Date.now();
    },
    requestTickets: (state, action) => {
      const { gamePk } = action.payload;
      if (state.games[gamePk] === undefined) {
        state.games[gamePk] = gameInitialState();
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
        state.games[gamePk] = gameInitialState();
      }
      const game = state.games[gamePk];
      payload.forEach(ticket => {
        state.tickets[ticket.pk] = {
          ...ticketInitialState(),
          ...ticket,
          lastUpdated: timestamp,
          invalid: false,
        };
      });
      game.isFetching = false;
      game.error = null;
      game.lastUpdated = timestamp;
      game.invalid = false;
      state.lastUpdated = timestamp;
      state.user = userPk;
    },
    failedFetchTickets: (state, action) => {
      const { timestamp, gamePk, error } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      game.isFetching = false;
      game.error = error;
      game.lastUpdated = timestamp;
      game.invalid = true;
      state.lastUpdated = timestamp;
    },
    receiveStatusUpdate: (state, action) => {
      const { payload, gamePk, timestamp } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        log.warn(`receiveStatusUpdate received unknown game ${gamePk}`);
        return;
      }
      game.isFetching = false;
      game.lastUpdated = timestamp;
      state.lastUpdated = timestamp;
      const { claimed } = payload;
      for (let pk in claimed) {
        const ticket = state.tickets[pk];
        if (ticket) {
          ticket.user = claimed[pk] ? claimed[pk] : null;
          ticket.lastUpdated = timestamp;
        }
      }
    },
    confirmAddTicket: (state, action) => {
      const { gamePk, ticketPk, user, timestamp } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      const ticket = state.tickets[ticketPk];
      if (ticket && ticket.user === null) {
        ticket.user = user.pk;
        ticket.lastUpdated = timestamp;
      }
    },
    confirmRemoveTicket: (state, action) => {
      const { timestamp, gamePk, ticketPk, user } = action.payload;
      const game = state.games[gamePk];
      if (!game) {
        return;
      }
      const ticket = state.tickets[ticketPk];
      if (ticket && ticket.user === user.pk) {
        ticket.user = null;
        ticket.lastUpdated = timestamp;
      }
    },
    requestTicketDetail: (state, action) => {
      const { ticketPk } = action.payload;
      const ticket = state.tickets[ticketPk];
      if (ticket) {
        ticket.isFetching = true;
      }
    },
    receiveTicketDetail: (state, action) => {
      const { timestamp, ticketPk, payload } = action.payload;
      const { tracks, checked } = payload;
      if (state.tickets[ticketPk]) {
        state.tickets[ticketPk] = {
          ...state.tickets[ticketPk],
          tracks,
          checked,
          invalid: false,
          isFetching: false,
          lastUpdated: timestamp,
        };
      }
    },
    failedFetchTicketDetail: (state, action) => {
      const { timestamp, ticketPk, error } = action.payload;
      const ticket = state.tickets[ticketPk];
      if (ticket) {
        ticket.isFetching = false;
        ticket.error = error;
        ticket.lastUpdated = timestamp;
      }
    },
    setChecked: (state, action) => {
      const { number, ticketPk, checked } = action.payload;
      const ticket = state.tickets[ticketPk];
      if (ticket) {
        let value = ticket.checked;
        const bit = 1 << number;
        if (checked) {
          ticket.checked = value | bit;
        } else {
          ticket.checked = value & ~bit;
        }
      }
    },
    toggleCell: (state, action) => {
      const { ticketPk, number } = action.payload;
      const ticket = state.tickets[ticketPk];
      if (ticket) {
        const bit = 1 << number;
        if ((ticket.checked & bit) === bit) {
          ticket.checked &= ~bit;
        } else {
          ticket.checked |= bit;
        }
      }
    }
  },
});

export function claimTicket({ gamePk, ticketPk }) {
  return api.claimCard({
    gamePk,
    ticketPk,
    success: ticketsSlice.actions.confirmAddTicket,
  });
}

export function releaseTicket({ gamePk, ticketPk }) {
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
    success: [
      receiveGameTickets,
      ticketsSlice.actions.receiveTickets,
    ],
  });
}

export function shouldFetchTickets(state, gamePk) {
  const { games, tickets, user } = state;
  const game = games[gamePk];
  if (!game) {
    return true;
  }
  if (user.pk !== tickets.user) {
    return true;
  }
  if (game.isFetching) {
    return false;
  }
  return game.invalid;
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
  if (game.isFetching || game.invalid) {
    return false;
  }
  const maxAge = Date.now() - tickets.updateInterval;
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

function fetchTicketDetail(userPk, gamePk, ticketPk) {
  return api.fetchCard({
    gamePk,
    ticketPk,
    before: ticketsSlice.actions.requestTicketDetail,
    success: ticketsSlice.actions.receiveTicketDetail,
    failure: ticketsSlice.actions.failedFetchTicketDetail,
  });
}

export function shouldFetchTicketDetail(state, gamePk, ticketPk) {
  const { tickets } = state;
  if (gamePk < 1 || ticketPk < 1) {
    return false;
  }
  const ticket = tickets.tickets[ticketPk];
  if (!ticket) {
    return false;
  }
  if (ticket.isFetching) {
    return false;
  }
  return ticket.invalid || ticket.tracks.length === 0;
}

export function fetchTicketDetailIfNeeded(gamePk, ticketPk) {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchTicketDetail(state, gamePk, ticketPk)) {
      return dispatch(fetchTicketDetail(state.user.pk, gamePk, ticketPk));
    }
    const ticket = state.tickets.tickets[ticketPk];
    return Promise.resolve(ticket);
  };
}

/* { gamePk, ticketPk,  row,  column,  number, checked } */
export function setChecked(args) {
  return api.setCardCellChecked({
    before: ticketsSlice.actions.setChecked,
    ...args
  });
}


userChangeListeners.receive.tickets = ticketsSlice.actions.receiveUser;
userChangeListeners.login.tickets = ticketsSlice.actions.receiveUser;
userChangeListeners.logout.tickets = ticketsSlice.actions.logoutUser;

export default ticketsSlice.reducer;
