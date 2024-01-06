import { createSlice } from '@reduxjs/toolkit';
import log from 'loglevel';

import { api } from '../endpoints';
import { userChangeListeners } from '../user/userSlice';

export const AvailableGroups = [
  "users",
  "creators",
  "hosts",
  "guests",
  "admin",
];

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

export const initialState = {
  users: [],
  guest: {
    tokens: [],
    isFetching: false,
    isSaving: false,
    invalid: true,
    error: null,
    lastUpdated: 0,
  },
  isFetching: false,
  isSaving: false,
  importing: null,
  invalid: true,
  error: null,
  lastUpdated: null,
  user: -1,
};

export const adminSlice = createSlice({
  name: 'admin',
  initialState,
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
    addUser: (state, action) => {
      const { email, password, username } = action.payload;
      let maxPk = 1;
      state.users.forEach((user) => {
        maxPk = Math.max(user.pk, maxPk);
      });
      state.users.push({
        pk: maxPk + 1,
        username,
        email,
        password,
        newUser: true,
        deleted: false,
        groups: {}
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
    savingModifiedUsers: (state) => {
      state.isSaving = true;
    },
    failedSaveModifiedUsers: (state, action) => {
      const { error } = action.payload;
      state.isSaving = false;
      state.error = error;
    },
    saveModifiedUsersDone: (state, action) => {
      const { payload, timestamp } = action.payload;
      const { added, modified, deleted } = payload;
      const users = [];
      const addMap = {};
      added.forEach(({ username, pk }) => addMap[username] = pk);
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
        } else if (user.newUser === true && addMap[user.username] !== undefined) {
          users.push({
            ...user,
            pk: addMap[user.username],
            password: "",
            modified: false,
            newUser: false
          });
        } else {
          users.push(user);
        }
      });
      state.users = users;
      state.lastUpdated = timestamp;
    },
    requestGuestLinks: (state) => {
      state.guest.isFetching = true;
    },
    receiveGuestLinks: (state, action) => {
      const { payload, timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.invalid = false;
      state.guest.lastUpdated = timestamp;
      state.guest.tokens = payload;
    },
    failedGetGuestLinks: (state, action) => {
      const { error, timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.lastUpdated = timestamp;
      state.guest.error = error;
    },
    requestCreateGuestToken: (state) => {
      state.guest.isFetching = true;
    },
    receiveCreateGuestToken: (state, action) => {
      const { payload, timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.tokens.push(payload.token);
      state.guest.lastUpdated = timestamp;
    },
    failedCreateGuestToken: (state, action) => {
      const { error, timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.lastUpdated = timestamp;
      state.guest.error = error;
    },
    requestDeleteGuestToken: (state) => {
      state.guest.isFetching = true;
    },
    receiveDeleteGuestToken: (state, action) => {
      const { token, timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.lastUpdated = timestamp;
      state.guest.tokens = state.guest.tokens.filter(item => item.jti !== token);
    },
    failedDeleteGuestToken: (state, action) => {
      const { timestamp } = action.payload;
      state.guest.isFetching = false;
      state.guest.lastUpdated = timestamp;
    },
    invalidateGuestTokens: state => {
      state.guest.invalid = true;
    },
    importingDatabase: (state, action) => {
      const { body, timestamp } = action.payload;
      const { filename } = body;
      state.importing = {
        ...ImportInitialFields,
        filename,
        timestamp,
      };
    },
    importDatabaseProgress: (state, action) => {
      const { payload = {}, done, timestamp } = action.payload;
      log.trace(`${Date.now()}: importDatabaseProgress timestamp=${timestamp} done=${done} pct=${payload?.pct} "${payload?.text}"`);
      state.importing = {
        ...state.importing,
        ...payload,
        done,
        timestamp
      };
    },
    importDatabaseFailed: (state, action) => {
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

function fetchUsers(_userId) {
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
      user => (user.modified === true || user.newUser === true)).map(user => {
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

function fetchGuestLinks(_userId) {
  return api.getGuestLinks({
    before: adminSlice.actions.requestGuestLinks,
    success: adminSlice.actions.receiveGuestLinks,
    failure: adminSlice.actions.failedGetGuestLinks,
  });
}

function shouldFetchGuestLinks(state) {
  const { admin } = state;
  if (admin.guest.isFetching || admin.guest.isSaving) {
    return false;
  }
  return admin.guest.invalid && admin.user > 0;
}

export function fetchGuestLinksIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchGuestLinks(state)) {
      return dispatch(fetchGuestLinks());
    }
    return Promise.resolve();
  };
}

export function createGuestToken() {
  return api.createGuestToken({
    before: adminSlice.actions.requestCreateGuestToken,
    success: adminSlice.actions.receiveCreateGuestToken,
    failure: adminSlice.actions.failedCreateGuestToken,
  });
}

export function deleteGuestToken(token) {
  return api.deleteGuestToken({
    token,
    before: adminSlice.actions.requestDeleteGuestToken,
    success: adminSlice.actions.receiveDeleteGuestToken,
    failure: adminSlice.actions.failedDeleteGuestToken,
  });
}

export function importDatabase(filename, data) {
  const body = { filename, data };
  return api.importDatabase({
    body,
    before: adminSlice.actions.importingDatabase,
    success: adminSlice.actions.importDatabaseProgress,
    failure: adminSlice.actions.importDatabaseFailed,
  });
}

export const { invalidateUsers, modifyUser, addUser,
  bulkModifyUsers, invalidateGuestTokens } = adminSlice.actions;
userChangeListeners.receive.admin = adminSlice.actions.receiveUser;
userChangeListeners.login.admin = adminSlice.actions.receiveUser;
userChangeListeners.logout.admin = adminSlice.actions.logoutUser;

export default adminSlice.reducer;
