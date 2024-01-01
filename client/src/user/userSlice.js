import { isEmail } from 'validator';
import { createSlice } from '@reduxjs/toolkit';
import { push } from '@lagunovsky/redux-react-router';

import { api } from '../endpoints';

export const userChangeListeners = {
  receive: {},
  login: {},
  logout: {},
};

export const initialState = {
  username: '',
  email: '',
  pk: -1,
  options: {
    colourScheme: 'blue',
    maxTickets: 2,
    columns: 5,
    rows: 3,
  },
  last_login: null,
  reset_expires: null,
  reset_token: null,
  isFetching: false,
  registering: false,
  didInvalidate: false,
  error: null,
  lastUpdated: null,
  activeGame: null,
  groups: {},
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  tokenFetching: false,
  guest: {
    isFetching: false,
    token: localStorage.getItem('guestToken'),
    valid: null,
    error: null,
    lastUpdated: null,
    username: localStorage.getItem('guestUsername'),
    password: localStorage.getItem('guestPassword'),
  },
  newUser: {
    isChecking: false,
    valid: false,
  },
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
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
      if (status === 401) {
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
    confirmLogoutUser: (state, action) => {
      state.isFetching = false;
      state.pk = -1;
      state.username = '';
      state.error = null;
      state.didInvalidate = true;
      state.accessToken = null;
      state.refreshToken = null;
      state.groups = {};
      state.guest.loggedIn = false;
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
      copyPayloadToState(user, state);
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
      const { accessToken, refreshToken } = payload;
      copyPayloadToState(payload, state);
      state.isFetching = false;
      state.registering = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.didInvalidate = false;
      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
        state.accessToken = accessToken;
      }
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
        state.refreshToken = refreshToken;
      }
      if (state.username === state.guest.username) {
        state.guest.loggedIn = true;
      }
    },
    failedFetchUser: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.registering = false;
      state.lastUpdated = timestamp;
      if (state.pk > 0) {
        state.error = error;
      }
      state.didInvalidate = true;
    },
    requestCheckNewUser: (state, action) => {
      const { body } = action.payload;
      const { username, email } = body;
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
      const { payload } = action.payload;
      const { username, email } = payload;
      state.newUser.existingUser = username === true;
      state.newUser.existingEmail = email === true;
      state.newUser.isChecking = false;
      state.newUser.valid = (username === false) && (email === false);
    },
    requestPasswordReset: (state, action) => {
      const { body } = action.payload;
      const { email } = body;
      state.email = email;
      state.isFetching = true;
    },
    confirmPasswordReset: (state, action) => {
      state.isFetching = false;
      state.error = null;
    },
    failedPasswordReset: (state, action) => {
      const { error } = action.payload;
      state.isFetching = false;
      state.error = error;
    },
    requestPasswordChange: (state, action) => {
      state.isFetching = true;
    },
    confirmPasswordChange: (state, action) => {
      const { body } = action.payload;
      const { email } = body;
      state.email = email;
      state.isFetching = false;
      state.error = null;
    },
    failedPasswordChange: (state, action) => {
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
      if (state.pk > 0) {
        state.error = error;
      }
      state.lastUpdated = timestamp;
      state.accessToken = null;
      state.isFetching = false;
    },
    receiveToken: (state, action) => {
      const { timestamp, payload } = action.payload;
      state.tokenFetching = false;
      state.accessToken = payload.accessToken;
      state.lastUpdated = timestamp;
    },
    requestCheckGuestToken: (state, action) => {
      const { body } = action.payload;
      const { token } = body;
      state.guest.token = token;
      state.guest.isFetching = true;
    },
    receiveCheckGuestToken: (state, action) => {
      const { timestamp, payload } = action.payload;
      const { success } = payload;
      state.guest.isFetching = false;
      state.guest.valid = success;
      state.guest.lastUpdated = timestamp;
      if (success === true) {
        localStorage.setItem('guestToken', state.guest.token);
      }
    },
    failedCheckGuestToken: (state, action) => {
      const { timestamp, error } = action.payload;
      state.guest.isFetching = false;
      state.guest.valid = false;
      state.guest.error = error;
      state.guest.lastUpdated = timestamp;
    },
    requestCreateGuestAccount: (state, action) => {
      state.isFetching = true;
    },
    failedCreateGuestAccount: (state, action) => {
      const { error, timestamp } = action.payload;
      state.guest.error = error;
      state.lastUpdated = timestamp;
      state.isFetching = false;
    },
    requestCreateGuestToken: (state, action) => {
      state.isFetching = true;
    },
    failedCreateGuestToken: (state, action) => {
      const { error, timestamp } = action.payload;
      state.error = error;
      state.lastUpdated = timestamp;
      state.isFetching = false;
    },
    receiveGuestUser: (state, action) => {
      const { payload } = action.payload;
      if (!payload) {
        return;
      }
      const { username, password } = payload;
      if (username) {
        localStorage.setItem('guestUsername', username);
        state.guest.username = username;
      }
      if (password) {
        localStorage.setItem('guestPassword', password);
        state.guest.password = password;
      }
      state.guest.loggedIn = true;
    },
    clearGuestDetails: (state, action) => {
      localStorage.removeItem("guestUsername");
      localStorage.removeItem("guestPassword");
    },
  },
});

function copyPayloadToState(payload, state) {
  const { username,
    email,
    pk,
    options,
    last_login = null,
    reset_expires = null,
    reset_token = null,
  } = payload;
  state.username = username;
  state.email = email;
  state.pk = pk;
  state.options = options;
  state.last_login = last_login;
  state.reset_expires = reset_expires;
  state.reset_token = reset_token;
  state.groups = {};
  if (payload.groups) {
    payload.groups.forEach(g => state.groups[g] = true);
  }
}

export const { setActiveGame, clearGuestDetails } = userSlice.actions;

function fetchUser() {
  const success = [
    userSlice.actions.receiveUser,
    ...Object.values(userChangeListeners.receive),
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
  const success = [
    userSlice.actions.receiveUser,
    ...Object.values(userChangeListeners.login),
  ];
  return api.login({
    body: user,
    noAccessToken: true,
    rejectErrors: false,
    before: userSlice.actions.requestLogin,
    failure: userSlice.actions.failedLoginUser,
    success,
  });
}

export function logoutUser() {
  const success = [
    userSlice.actions.confirmLogoutUser,
    ...Object.values(userChangeListeners.logout),
  ];
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  return api.logout({
    success,
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
    before: userSlice.actions.requestPasswordReset,
    success: userSlice.actions.confirmPasswordReset,
    failure: userSlice.actions.failedPasswordReset,
  });
}

export function changeUserPassword(user) {
  return api.modifyMyself({
    body: user,
    rejectErrors: false,
    before: userSlice.actions.requestPasswordChange,
    success: userSlice.actions.confirmPasswordChange,
    failure: userSlice.actions.failedPasswordChange,
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

export function checkGuestToken(token) {
  return api.checkGuestToken({
    body: { token },
    noAccessToken: true,
    rejectErrors: false,
    before: userSlice.actions.requestCheckGuestToken,
    success: userSlice.actions.receiveCheckGuestToken,
    failure: userSlice.actions.failedCheckGuestToken,
  });
}

export function createGuestAccount(token, nextPage) {
  const changePage = () => push(nextPage);

  const success = [
    userSlice.actions.receiveUser,
    userSlice.actions.receiveGuestUser,
    ...Object.values(userChangeListeners.login),
    changePage,
  ];

  return api.createGuestAccount({
    body: { token },
    noAccessToken: true,
    rejectErrors: false,
    before: userSlice.actions.requestCreateGuestAccount,
    success,
    failure: userSlice.actions.failedCreateGuestAccount,
  });
}

export default userSlice.reducer;

api.actions.refreshAccessToken = refreshAccessToken;
