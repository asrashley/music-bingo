import { createSlice } from '@reduxjs/toolkit';

import { api } from '../endpoints';

const gameAdditionalFields = {
  tracks: [],
  isFetchingDetail: false,
  invalidDetail: true,
  lastUpdated: null,
  isModifying: false,
};
Object.freeze(gameAdditionalFields);

const dateOrder = (a, b) => {
  if (a.start < b.start) {
    return -1;
  } else if (a.start > b.start) {
    return 1;
  }
  return 0;
};

export const gamesSlice = createSlice({
  name: 'games',
  initialState: {
    games: {},
    order: [],
    pastOrder: [],
    user: -1,
    isFetching: false,
    invalid: true,
    error: null,
    lastUpdated: null,
  },
  reducers: {
    invalidateGames: state => {
      state.invalid = true;
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
        state.games[game.pk] = {
          ...game,
          ...gameAdditionalFields,
        };
        state.order.push(game.pk);
      });
      past.forEach(game => {
        state.games[game.pk] = {
          ...game,
          ...gameAdditionalFields,
        };
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
    modifyGame: (state, action) => {
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk].isModifying = true;
    },
    failedModifyGame: (state, action) => {
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk].isModifying = false;
    },
    receiveDetail: (state, action) => {
      const { timestamp, payload } = action.payload;
      if (!state.games[payload.pk]) {
        console.log('failed find game PK');
        console.dir(payload);
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
      const { gamePk } = action.payload;
      if (!state.games[gamePk]) {
        return;
      }
      state.games[gamePk] = {
        ...state.games[gamePk],
        tracks: [],
        isFetchingDetail: false,
        invalidDetail: true,
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
  if (games.isFetching) {
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
    const game = state.games.games[gamePk];
    return Promise.resolve(game ? game : null);
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
    success: gamesSlice.actions.gameDeleted,
    failure: gamesSlice.actions.failedModifyGame,
  });
}

export const { invalidateGames, invalidateGameDetail } = gamesSlice.actions;

export const initialState = gamesSlice.initialState;

export default gamesSlice.reducer;
