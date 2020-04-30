import { createSlice } from '@reduxjs/toolkit';

import { getUsersListURL } from '../endpoints';

export const AvailableGroups = [
  "users",
  "creator",
  "host",
  "admin",
];

export const adminSlice = createSlice({
  name: 'admin',
  initialState: {
    users: [],
    isFetching: false,
    invalid: true,
    error: null,
    lastUpdated: null,
    user: -1,
  },
  reducers: {
    invalidateUsers: state => {
      state.invalid = true;
    },
    requestUsers: state => {
      state.isFetching = true;
    },
    receiveUsers: (state, action) => {
      const { timestamp, users } = action.payload;
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.invalid = false;
      state.users = users.map(user => {
        const groups = {};
        user.groups.forEach(g => groups[g] = true);
        return {
          ...user,
          groups
        };
      });
    },
    failedFetchUsers: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.invalid = true;
    },
  },
});

function fetchUsers(userId) {
  return dispatch => {
    dispatch(adminSlice.actions.requestUsers());
    return fetch(getUsersListURL, {
      cache: "no-cache",
      credentials: 'same-origin',
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        const result = {
          error: `${response.status}: ${response.statusText}`,
          userId,
          timestamp: Date.now()
        };
        adminSlice.actions.failedFetchUsers(result);
        return Promise.reject(result);
      })
      .then(users => dispatch(adminSlice.actions.receiveUsers({ users, userId, timestamp: Date.now() })));
  };
}

function shouldFetchUsers(state) {
  const { admin, user } = state;
  if (admin.isFetching) {
    return false;
  }
  return admin.invalid || user.pk !== admin.user;
}

export function fetchUsersIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchUsers(state)) {
      return dispatch(fetchUsers(state.user.pk));
    }
    return Promise.resolve();
  };
}

export const { invalidateUsers } = adminSlice.actions;

export const initialState = adminSlice.initialState;

export default adminSlice.reducer;
