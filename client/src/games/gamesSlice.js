import { createSlice } from '@reduxjs/toolkit';
import log from 'loglevel';

import { api } from '../endpoints';
import { userChangeListeners } from '../user/userSlice';

const gameAdditionalFields = {
  tracks: [],
  ticketOrder: [],
  isFetchingDetail: false,
  invalidDetail: true,
  lastUpdated: 0,
  isModifying: false,
};
Object.freeze(gameAdditionalFields);

export const gameInitialFields = {
  ...gameAdditionalFields,
  end: "",
  id: "",
  pk: -1,
  start: "",
  title: "",
  options: {
    backgrounds: [],
    colour_scheme: '',
    columns: 5,
    rows: 3,
    number_of_cards: 0,
  },
  userCount: 0,
};
Object.freeze(gameInitialFields);

export const ImportInitialFields = {
  added: {},
  done: false,
  errors: [],
  filename: '',
  text: '',
  timestamp: 0,
  numPhases: 1,
  pct: 0,
  phase: 1,
};
Object.freeze(ImportInitialFields);

const dateOrder = (a, b) => {
  if (a.start < b.start) {
    return -1;
  } else if (a.start > b.start) {
    return 1;
  }
  return 0;
};

export const initialState = {
  games: {},
  gameIds: {},
  order: [],
  pastOrder: [],
  user: -1,
  isFetching: false,
  invalid: true,
  error: null,
  lastUpdated: 0,
  popularity: {
    vertical: true,
  },
  importing: null,
};

export const gamesSlice = createSlice({
  name: 'games',
  initialState,
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.user && state.isFetching === false) {
        state.invalid = true;
        state.games = {};
        state.gameIds = {};
        state.order = [];
        state.pastOrder = [];
        state.user = user.pk;
      }
    },
    invalidateGames: state => {
      state.invalid = true;
      state.games = {};
      state.gameIds = {};
      state.order = [];
      state.pastOrder = [];
    },
    logoutUser: state => {
      state.invalid = true;
      state.games = {};
      state.gameIds = {};
      state.order = [];
      state.pastOrder = [];
      state.user = -1;
    },
    requestGames: state => {
      state.isFetching = true;
    },
    receiveGames: (state, action) => {
      const { timestamp, payload, user } = action.payload;
      const { games, past } = payload;
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.invalid = false;
      state.user = user.pk;
      state.games = {};
      state.order = [];
      state.pastOrder = [];
      games.forEach(game => {
        if (state.games[game.pk]) {
          game = {
            ...state.games[game.pk],
            ...game,
          };
        }
        state.games[game.pk] = {
          ...gameAdditionalFields,
          ...game,
        };
        state.gameIds[game.id] = game.pk;
        state.order.push(game.pk);
      });
      past.forEach(game => {
        if (state.games[game.pk]) {
          game = {
            ...state.games[game.pk],
            ...game,
          };
        }
        state.games[game.pk] = {
          ...gameAdditionalFields,
          ...game,
        };
        state.gameIds[game.id] = game.pk;
        state.pastOrder.push(game.pk);
      });
    },
    failedFetchGames: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.invalid = true;
    },
    requestDetail: (state, action) => {
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk].isFetchingDetail = true;
    },
    receiveGameTickets: (state, action) => {
      const { payload, timestamp, gamePk } = action.payload;
      if (state.games[gamePk] === undefined) {
        state.games[gamePk] = {
          ...gameInitialFields
        };
      }
      const game = state.games[gamePk];
      game.ticketOrder = [];
      payload.forEach(ticket => {
        game.ticketOrder.push(ticket.pk);
      });
      game.isFetching = false;
      game.error = null;
      game.lastUpdated = timestamp;
      game.invalid = false;
    },
    modifyGame: (state, action) => {
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk].isModifying = true;
    },
    failedModifyGame: (state, action) => {
      const { gamePk } = action.payload;
      log.debug(`Failed to modify game "${gamePk}"`);
      if (!state.games[gamePk]) {
        log.warn(`Failed to modify unknown game "${gamePk}"`);
        return;
      }
      state.games[gamePk].isModifying = false;
    },
    receiveDetail: (state, action) => {
      const { timestamp, payload } = action.payload;
      if (!state.games[payload.pk]) {
        log.warn(`received detail for unknown game ${payload.pk}`);
        return;
      }
      state.games[payload.pk] = {
        ...state.games[payload.pk],
        ...payload,
        isFetchingDetail: false,
        invalidDetail: false,
        lastUpdated: timestamp,
      };
    },
    receiveGameModification: (state, action) => {
      const { timestamp, payload, gamePk } = action.payload;
      if (!state.games[gamePk]) {
        log.warn(`received game modification for unknown game "${gamePk}"`);
        return;
      }
      const updateOrder = state.games[gamePk].start !== payload.game.start ||
        state.games[gamePk].end !== payload.game.end;
      state.games[gamePk] = {
        ...state.games[gamePk],
        ...payload.game,
        isModifying: false,
        lastUpdated: timestamp,
      };
      if (updateOrder) {
        const order = [];
        const pastOrder = [];
        const now = new Date().toISOString();
        let today = new Date();
        today.setHours(0);
        today.setMinutes(0);
        today.setMilliseconds(0);
        today = today.toISOString();
        for (let pk in state.games) {
          const game = state.games[pk];
          if (game.start >= today && game.end > now) {
            order.push(game);
          } else {
            pastOrder.push(game);
          }
        }
        order.sort(dateOrder);
        pastOrder.sort(dateOrder);
        state.order = order.map(g => g.pk);
        state.pastOrder = pastOrder.map(g => g.pk);
      }
    },
    receiveGameDeleted: (state, action) => {
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        log.warn(`receiveGameDeleted for an unknown game ${gamePk}`);
        return;
      }
      delete state.games[gamePk];
      state.order = state.order.filter(pk => pk !== gamePk);
      state.pastOrder = state.pastOrder.filter(pk => pk !== gamePk);
    },
    failedFetchDetail: (state, action) => {
      const { gamePk, error, timestamp } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk] = {
        ...state.games[gamePk],
        isFetchingDetail: false,
        invalidDetail: true,
        lastUpdated: timestamp,
        error,
      };
    },
    invalidateGameDetail: (state, action) => {
      const { game } = action.payload;
      if (!state.games[game.pk]) {
        return;
      }
      state.games[game.pk] = {
        ...state.games[game.pk],
        tracks: [],
        ticketOrder: [],
        isFetchingDetail: false,
        invalidDetail: true,
      };
    },
    setPopularityOptions: (state, action) => {
      state.popularity = {
        ...state.popularity,
        ...action.payload,
      };
    },
    importingGame: (state, action) => {
      const { body, timestamp } = action.payload;
      const { filename } = body;
      state.importing = {
        ...ImportInitialFields,
        filename,
        timestamp,
      };
    },
    importGameProgress: (state, action) => {
      const { payload, timestamp } = action.payload;
      state.importing = {
        ...state.importing,
        ...payload,
        timestamp
      };
    },
    importGameFailed: (state, action) => {
      const { error, timestamp } = action.payload;
      let { errors } = action.payload;
      if (!errors) {
        if (error) {
          errors = [error];
        } else {
          errors = ["Unknown Error"];
        }
      }
      state.importing = {
        ...state.importing,
        done: true,
        errors,
        timestamp
      };
    },
  },
});

function fetchGames(userId) {
  return api.getGamesList({
    before: gamesSlice.actions.requestGames,
    failure: gamesSlice.actions.failedFetchGames,
    success: gamesSlice.actions.receiveGames,
  });
}

function shouldFetchGames(state) {
  const { games, user } = state;
  if (games.isFetching || user.pk < 1) {
    return false;
  }
  return games.invalid || user.pk !== games.user;
}

export function fetchGamesIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchGames(state)) {
      return dispatch(fetchGames(state.user.pk));
    }
    return Promise.resolve();
  };
}

function fetchDetail(userPk, gamePk) {
  return api.getGameDetail({
    gamePk,
    before: gamesSlice.actions.requestDetail,
    failure: gamesSlice.actions.failedFetchDetail,
    success: gamesSlice.actions.receiveDetail
  });
}

function shouldFetchDetail(state, gamePk) {
  const { games, user } = state;
  if (gamePk < 1 || user.pk < 1) {
    return false;
  }
  const game = games.games[gamePk];
  if (!game) {
    return false;
  }
  if (user.pk !== games.user) {
    return true;
  }
  if (game.isFetchingDetail) {
    return false;
  }
  return game.invalidDetail;
}

export function fetchDetailIfNeeded(gamePk) {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchDetail(state, gamePk)) {
      return dispatch(fetchDetail(state.user.pk, gamePk));
    }
    return Promise.resolve(state.games.games[gamePk]);
  };
}

export function modifyGame(game) {
  const gamePk = game.pk;
  return api.modifyGame({
    gamePk,
    body: game,
    before: gamesSlice.actions.modifyGame,
    success: gamesSlice.actions.receiveGameModification,
    failure: gamesSlice.actions.failedModifyGame,
  });
}

export function deleteGame(game) {
  const gamePk = game.pk;
  return api.deleteGame({
    body: game,
    gamePk,
    before: gamesSlice.actions.modifyGame,
    success: gamesSlice.actions.receiveGameDeleted,
    failure: gamesSlice.actions.failedModifyGame,
  });
}

export function importGame(filename, data) {
  const body = {filename, data};
  return api.importGame({
    body,
    before: gamesSlice.actions.importingGame,
    success: gamesSlice.actions.importGameProgress,
    failure: gamesSlice.actions.importGameFailed,
  });
}

export const {
  invalidateGames, invalidateGameDetail, receiveGameTickets, setPopularityOptions,
} = gamesSlice.actions;

userChangeListeners.receive.games = gamesSlice.actions.receiveUser;
userChangeListeners.login.games = gamesSlice.actions.receiveUser;
userChangeListeners.logout.games = gamesSlice.actions.logoutUser;

export default gamesSlice.reducer;
