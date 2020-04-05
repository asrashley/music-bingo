import { createSlice } from '@reduxjs/toolkit';
import { Enumify } from 'enumify';

import { getGamesURL, getGameDetailURL } from '../endpoints';

export const gamesSlice = createSlice({
    name: 'games',
    initialState: {
        games: {},
        order: [],
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
            const { timestamp, games, userId } = action.payload;
            state.isFetching = false;
            state.error = null;
            state.lastUpdated = timestamp;
            state.invalid = false;
            state.user = userId;
            state.games = {}
            state.order = [];
            games.forEach(game => {
              state.games[game.pk] = game;
              state.games[game.pk].tracks = [];
              state.games[game.pk].isFetchingDetail = false;
              state.games[game.pk].invalidDetail = true;
                state.order.push(game.pk);
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

      receiveDetail: (state, action) => {
        const { timestamp, game, gamePk } = action.payload;
        if (!state.games[gamePk]) {
          return;
        }
        state.games[gamePk] = {
          ...state.games[gamePk],
          ...game,
          isFetchingDetail: false,
          invalidDetail: false,
          lastUpdated: timestamp,
        }
      },
    },
});

function fetchGames(userId) {
    return dispatch => {
        dispatch(gamesSlice.actions.requestGames());
        return fetch(getGamesURL, {
            cache: "no-cache",
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(games => dispatch(gamesSlice.actions.receiveGames({ games, userId, timestamp: Date.now() })))
            .catch(error => dispatch(gamesSlice.actions.failedFetchGames({ error, userId, timestamp: Date.now() })));
    };
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
  return dispatch => {
    dispatch(gamesSlice.actions.requestDetail({ gamePk }));
    return fetch(getGameDetailURL(gamePk), {
      cache: "no-cache",
      credentials: 'same-origin',
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        return Promise.reject({ error: `${response.status}: ${response.statusText}` });
      })
      .then((result) => {
        const { error } = result;
        if (error === undefined) {
          return dispatch(gamesSlice.actions.receiveDetail({ game: result, gamePk, userPk, timestamp: Date.now() }));
        }
        return dispatch(gamesSlice.actions.failedFetchDetail({ gamePk, error, timestamp: Date.now() }));
      });
  };
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
  console.log("fetchDetailIfNeeded");
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchDetail(state, gamePk)) {
      return dispatch(fetchDetail(state.user.pk, gamePk));
    }
    const game = state.games.games[gamePk];
    return Promise.resolve(game ? game : null);
  };
}


export const { invalidateGames } = gamesSlice.actions;

export const initialState = gamesSlice.initialState;

export default gamesSlice.reducer;
