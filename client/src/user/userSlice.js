import { isEmail } from 'validator';
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
    registering: false,
    didInvalidate: false,
    error: null,
    lastUpdated: null,
    activeGame: null,
    groups: {
    },
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    tokenFetching: false,
    newUser: {
      isChecking: false,
      valid: false,
    },
  },
  reducers: {
    requestUser: (state, action) => {
      state.isFetching = true;
    },
    requestLogin: (state, action) => {
      const { body } = action.payload;
      const { username } = body;
      state.isFetching = true;
      state.username = username;
    },
    failedLoginUser: (state, action) => {
      const { body, status, error, timestamp } = action.payload;
      if (status === 401){
        const { username } = body;
        if (isEmail(username)) {
          state.error = 'Email address or password is incorrect';
        } else {
          state.error = 'Username or password is incorrect';
        }
      } else {
        state.error = error;
      }
      state.lastUpdated = timestamp;
      state.isFetching = false;
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
    registeringUser: (state, action) => {
      const { body } = action.payload;
      const { username, email } = body;
      state.registering = true;
      state.email = email;
      state.username = username;
    },
    failedRegisterUser: (state, action) => {
      const { error, timestamp } = action.payload;
      state.registering = false;
      state.error = error;
      state.lastUpdated = timestamp;
    },
    userRegistered: (state, action) => {
      const { payload, timestamp } = action.payload;
      const { user, accessToken, refreshToken } = payload;
      for (let key in user) {
        const value = user[key];
        if (key === 'timestamp' || value === undefined) {
          continue;
        }
        state[key] = value;
      }
      state.groups = {};
      user.groups.forEach(g => state.groups[g] = true);
      state.isFetching = false;
      state.registering = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.didInvalidate = false;
      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
      }
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
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
      state.groups = {};
      payload.groups.forEach(g => state.groups[g] = true);
      state.isFetching = false;
      state.registering = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.didInvalidate = false;
      if (payload.accessToken) {
        localStorage.setItem('accessToken', payload.accessToken);
      }
      if (payload.refreshToken) {
        localStorage.setItem('refreshToken', payload.refreshToken);
      }
    },
    failedFetchUser: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.registering = false;
      state.lastUpdated = timestamp;
      if (state.pk > 0){
        state.error = error;
      }
      state.didInvalidate = true;
    },
    requestCheckNewUser: (state, action) => {
      const { body } = action.payload;
      const {username, email} = body;
      state.newUser = {
        username,
        email,
        isChecking: true,
        isValid: null,
      };
    },
    failedCheckNewUser: (state, action) => {
      state.newUser.isChecking = false;
      state.newUser.valid = false;
    },
    successCheckNewUser: (state, action) => {
      state.newUser.isChecking = false;
      state.newUser.valid = true;
    },
    failedResetUser: (state, action) => {
      const { error } = action.payload;
      state.isFetching = false;
      state.error = error;
    },
    confirmPasswordReset: (state, action) => {
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
    rejectErrors: false,
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
  return api.checkUser({
    body: { username, email },
    before: userSlice.actions.requestCheckNewUser,
    failure: userSlice.actions.failedCheckNewUser,
    success: userSlice.actions.successCheckNewUser,
  });
}

export function loginUser(user) {
  return api.login({
    body: user,
    noAccessToken: true,
    before: userSlice.actions.requestLogin,
    failure: userSlice.actions.failedLoginUser,
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
    rejectErrors: false,
    before: userSlice.actions.registeringUser,
    success: userSlice.actions.userRegistered,
    failure: userSlice.actions.failedRegisterUser
  });
}

export function passwordResetUser(user) {
  return api.passwordReset({
    body: user,
    noAccessToken: true,
    rejectErrors: false,
    success: userSlice.actions.confirmPasswordReset,
    failure: userSlice.actions.failedResetUser
  });
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
