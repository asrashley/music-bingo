import { createSlice } from '@reduxjs/toolkit';
import { checkUserURL, getUserURL, registerUserURL, getLogoutURL, passwordResetUserURL } from '../endpoints';

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
    },
    receiveUser: (state, action) => {
      const { timestamp, user } = action.payload;
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.didInvalidate = false;
      state.pk = user.pk;
      state.username = user.username;
      state.email = user.email;
      state.groups = {};
      user.groups.forEach(g => state.groups[g] = true);
      state.options = user.options;
      if (user.users !== undefined) {
        state.users = user.users;
      }
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
  },
});

export const { setActiveGame } = userSlice.actions;

function fetchUser() {
  return dispatch => {
    dispatch(userSlice.actions.requestUser());
    return fetch(getUserURL)
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        const result = {
          error: `${response.status}: ${response.statusText}`,
          timestamp: Date.now()
        };
        dispatch(userSlice.actions.failedFetchUser(result));
        return Promise.reject(result);
      })
      .then((user) => {
        if (user.error) {
          dispatch(userSlice.actions.failedFetchUser({
            error: user.error,
            timestamp: Date.now()
          }));
        } else {
          dispatch(userSlice.actions.receiveUser({
            user,
            timestamp: Date.now()
          }));
        }
      });
  };
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
  return (dispatch, getState) => {
    return fetch(checkUserURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        return {
          found: false,
          error: `${response.status}: ${response.statusText}`,
        };
      });
  };
}

export function loginUser(user) {
  return (dispatch) => {
    return fetch(getUserURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      cache: "no-cache",
      credentials: 'same-origin',
      body: JSON.stringify(user),
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        const result = {
          error: `${response.status}: ${response.statusText}`,
          timestamp: Date.now()
        };
        dispatch(userSlice.actions.failedFetchUser(result));
        return Promise.reject(result);
      })
      .then((user) => {
        const { error } = user;
        if (error) {
          dispatch(userSlice.actions.failedFetchUser({
            error,
            timestamp: Date.now()
          }));
        } else {
          dispatch(userSlice.actions.receiveUser({
            user,
            timestamp: Date.now()
          }));
        }
        return ({ success: true, user });
      });
  };
}

export function logoutUser() {
  return (dispatch, getState) => {
    const { user } = getState();
    return fetch(getLogoutURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user.username),
    })
      .then(() => dispatch(userSlice.actions.confirmLogoutUser()));
  };
}

export function registerUser(user) {
  return (dispatch) => {
    return fetch(registerUserURL, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user),
    })
      .then(response => response.json())
      .then((result) => {
        const { user, error, success } = result;
        if (error) {
          return ({ user, error, success });
        }
        dispatch(userSlice.actions.receiveUser({ user, timestamp: Date.now() }));
        return ({ user, success });
      });
  };
}

export function passwordResetUser(user) {
  const { email } = user;
  return (dispatch, getState) => {
    const state = getState();
    if (userIsLoggedIn(state)) {
      return Promise.reject("User is currently logged in");
    }
    return fetch(passwordResetUserURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user),
    })
      .then((response) => {
        if (!response.ok) {
          const result = {
            error: `${response.status}: ${response.statusText}`,
            timestamp: Date.now()
          };
          dispatch(userSlice.actions.failedResetUser(result));
          return Promise.reject(result);
        }
        return response.json();
      })
      .then((result) => {
        const { error, success } = result;
        if (error) {
          return ({ email, error, success });
        }
        dispatch(userSlice.actions.confirmLogoutUser());
        return ({ email, success });
      });
  };
}

export const initialState = userSlice.initialState;

export const userIsLoggedIn = state => (state.user.pk > 0 && state.user.error === null && state.user.isFetching === false);

export default userSlice.reducer;
