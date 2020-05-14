import { createSlice } from '@reduxjs/toolkit';
import { api } from '../endpoints';

export const userChangeListeners = {};

export const userSlice = createSlice({
  name: 'user',
  initialState: {
    username: '',
    email: '',
    pk: -1,
    options: {
      colourScheme: 'blue',
      maxTickets: 2,
      columns: 5,
      rows: 3,
    },
    isFetching: false,
    didInvalidate: false,
    error: null,
    lastUpdated: null,
    activeGame: null,
    groups: {
    },
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    tokenFetching: false,
  },
  reducers: {
    requestUser: state => {
      state.isFetching = true;
    },
    confirmLogoutUser: state => {
      state.isFetching = false;
      state.pk = -1;
      state.username = '';
      state.error = null;
      state.didInvalidate = true;
      state.accessToken = null;
      state.refreshToken = null;
    },
    receiveUser: (state, action) => {
      const { timestamp, payload } = action.payload;
      for (let key in payload) {
        const value = payload[key];
        if (key === 'timestamp' || value === undefined) {
          continue;
        }
        state[key] = value;
      }
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.didInvalidate = false;
      if (payload.accessToken) {
        localStorage.setItem('accessToken', payload.accessToken);
      }
      if (payload.refreshToken) {
        localStorage.setItem('refreshToken', payload.refreshToken);
      }
      state.groups = {};
      payload.groups.forEach(g => state.groups[g] = true);
    },
    failedFetchUser: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.didInvalidate = true;
    },
    failedResetUser: (state, action) => {
      const { error } = action.payload;
      state.isFetching = false;
      state.error = error;
    },
    setActiveGame: (state, action) => {
      let gamePk = action.payload;
      if (typeof (gamePk) === "string") {
        gamePk = parseInt(gamePk);
      }
      if (typeof (gamePk) === "number" && !isNaN(gamePk)) {
        state.activeGame = gamePk;
      }
    },
    requestToken: (state) => {
      state.tokenFetching = true;
    },
    failedFetchToken: (state, action) => {
      const { timestamp, error } = action.payload;
      state.tokenFetching = false;
      state.error = error;
      state.lastUpdated = timestamp;
      state.accessToken = null;
    },
    receiveToken: (state, action) => {
      const { timestamp, payload } = action.payload;
      state.tokenFetching = false;
      state.accessToken = payload.accessToken;
      state.lastUpdated = timestamp;
    },
  },
});

export const { setActiveGame } = userSlice.actions;

function fetchUser() {
  const success = [
    userSlice.actions.receiveUser,
    ...Object.values(userChangeListeners),
  ];
  return api.getUserInfo({
    before: userSlice.actions.requestUser,
    failure: userSlice.actions.failedFetchUser,
    success,
  });
}

function shouldFetchUser(state) {
  const { user } = state;
  if (user.pk <= 0) {
    return true;
  }
  if (user.isFetching) {
    return false;
  }
  return user.didInvalidate;
}

export function fetchUserIfNeeded() {
  return (dispatch, getState) => {
    if (shouldFetchUser(getState())) {
      return dispatch(fetchUser());
    }
    return Promise.resolve();
  };
}

export function checkUser({ username, email }) {
  function failedCheckUser(response) {
    return {
      found: false,
      error: response.error,
    };
  }
  return api.checkUser({
    body: { username, email },
    failure: failedCheckUser
  });
}

export function loginUser(user) {
  return api.login({
    body: user,
    noAccessToken: true,
    before: userSlice.actions.requestUser,
    failure: userSlice.actions.failedFetchUser,
    success: userSlice.actions.receiveUser
  });
}

export function logoutUser() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  return api.logout({
    success: userSlice.actions.confirmLogoutUser,
    failure: userSlice.actions.failedLogout
  });
}

export function registerUser(user) {
  return api.registerUser({
    body: user,
    noAccessToken: true,
    success: userSlice.actions.receiveUser,
    failure: userSlice.actions.failedRegisterUser
  });
}

export function passwordResetUser(user) {
  return (dispatch, getState) => {
    const { user } = getState();
    if (user.isFetching === true) {
      return Promise.reject("User fetch is in progress");
    }
    if (user.pk > 0 && user.error === null) {
      return Promise.reject("User is currently logged in");
    }
    return api.passwordReset({
      body: user,
      noAccessToken: true,
      success: userSlice.actions.confirmPasswordReset,
      failure: userSlice.actions.failedPasswordReset
    });
  };
}

export function refreshAccessToken(refreshToken) {
  return api.refreshToken({
    refreshToken,
    before: userSlice.actions.requestToken,
    success: userSlice.actions.receiveToken,
    failure: userSlice.actions.failedFetchToken,
  });
}

export const initialState = userSlice.initialState;

export default userSlice.reducer;

api.actions.refreshAccessToken = refreshAccessToken;
