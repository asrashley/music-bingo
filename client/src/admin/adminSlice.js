import { createSlice } from '@reduxjs/toolkit';

import { api } from '../endpoints';
import { userChangeListeners } from '../user/userSlice';

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
    isSaving: false,
    invalid: true,
    error: null,
    lastUpdated: null,
    user: -1,
  },
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.pk && state.isFetching === false) {
        state.user = user.pk;
        state.users = [];
        state.invalid = true;
      }
    },
    logoutUser: (state) => {
      state.user = -1;
      state.users = [];
      state.invalid = true;
    },
    invalidateUsers: state => {
      state.invalid = true;
    },
    requestUsers: state => {
      state.isFetching = true;
    },
    receiveUsers: (state, action) => {
      const { timestamp, payload } = action.payload;
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.invalid = false;
      state.users = payload.map(user => {
        const groups = {};
        user.groups.forEach(g => groups[g] = true);
        return {
          ...user,
          groups,
          password: '',
          modified: false,
          deleted: false,
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
    modifyUser: (state, action) => {
      const { pk, field, value } = action.payload;
      state.users.forEach((user, idx) => {
        if (user.pk !== pk) {
          return;
        }
        state.users[idx] = {
          ...user,
          [field]: value,
          modified: true,
        };
      });
    },
    bulkModifyUsers: (state, action) => {
      const { users, field, value } = action.payload;
      state.users.forEach((user, idx) => {
        if (users.includes(user.pk)) {
          state.users[idx] = {
            ...user,
            [field]: value,
            modified: true,
          };
        }
      });
    },
    savingModifiedUsers: (state, action) => {
      state.isSaving = true;
    },
    failedSaveModifiedUsers: (state, action) => {
      const { error } = action.payload;
      state.isSaving = false;
      state.error = error;
    },
    saveModifiedUsersDone: (state, action) => {
      const { payload, timestamp } = action.payload;
      const { modified, deleted } = payload;
      const users = [];
      state.isSaving = false;
      state.users.forEach((user) => {
        if (deleted.includes(user.pk)) {
          return;
        }
        if (modified.includes(user.pk)) {
          users.push({
            ...user,
            modified: false,
          });
        } else {
          users.push(user);
        }
      });
      state.users = users;
      state.lastUpdated = timestamp;
    },
  },
});

function fetchUsers(userId) {
  return api.getUsersList({
    before: adminSlice.actions.requestUsers,
    success: adminSlice.actions.receiveUsers,
    failure: adminSlice.actions.failedFetchUsers,
  });
}

function shouldFetchUsers(state) {
  const { admin, user } = state;
  if (admin.isFetching || admin.isSaving) {
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

export function saveModifiedUsers() {
  return (dispatch, getState) => {
    const state = getState();
    const modified = state.admin.users.filter(
      user => user.modified === true).map(user => {
        const groups = [];
        for (let g in user.groups) {
          if (user.groups[g] === true) {
            groups.push(g);
          }
        }
        return { ...user, groups };
      });
    if (modified.length === 0) {
      return Promise.resolve({});
    }
    return dispatch(api.modifyUsers({
      body: modified,
      before: adminSlice.actions.savingModifiedUsers,
      success: adminSlice.actions.saveModifiedUsersDone,
      failure: adminSlice.actions.failedSaveModifiedUsers,
    }));
  };
}
export const { invalidateUsers, modifyUser, bulkModifyUsers } = adminSlice.actions;
userChangeListeners.receive.admin = adminSlice.actions.receiveUser;
userChangeListeners.login.admin = adminSlice.actions.receiveUser;
userChangeListeners.logout.admin = adminSlice.actions.logoutUser;

export const initialState = adminSlice.initialState;

export default adminSlice.reducer;
