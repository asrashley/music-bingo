import { createSlice } from '@reduxjs/toolkit';

import { userChangeListeners } from '../user/userSlice';
import { api } from '../endpoints';

export function DirectoryInitialState() {
  return ({
    parent: null,
    pk: -1,
    title: '',
    songs: [],
    directories: [],
    lastUpdated: null,
    isFetching: false,
    didInvalidate: false,
    invalid: false,
    expanded: false,
  });
}

export const directoriesSlice = createSlice({
  name: 'directories',
  initialState: {
    directories: {},
    user: -1,
    isFetching: false,
    didInvalidate: false,
    error: null,
    lastUpdated: null,
    invalid: true,
    sortOptions: {
      ascending: true,
      field: 'title'
    }
  },
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.pk && state.isFetching === false) {
        state.directories = {};
        state.user = user.pk;
      }
    },
    logoutUser: (state, action) => {
      state.games = {};
      state.Directories = {};
      state.user = -1;
    },
    requestDirectories: (state, action) => {
      state.isFetching = true;
    },
    receiveDirectories: (state, action) => {
      const { payload, timestamp, userPk } = action.payload;
      payload.forEach(directory => {
        state.directories[directory.pk] = {
          ...DirectoryInitialState(),
          ...directory,
          invalid: false
         };
      });
      state.user = userPk;
      state.lastUpdated = timestamp;
      state.invalid = false;
      state.isFetching = false;
    },
    failedFetchDirectories: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.error = error;
      state.lastUpdated = timestamp;
      state.invalid = true;
    },
    requestDirectoryDetail: (state, action) => {
      const { dirPk } = action.payload;
      const directory = state.directories[dirPk];
      if (directory !== undefined) {
        directory.isFetching = true;
      }
    },
    failedFetchDirectoryDetail: (state, action) => {
      const { dirPk, error, timestamp } = action.payload;
      const directory = state.directories[dirPk];
      if (directory !== undefined) {
        directory.isFetching = false;
        directory.invalid = true;
        directory.error = error;
        directory.lastUpdated = timestamp;
      }
    },
    receiveDirectoryDetail: (state, action) => {
      const { dirPk, payload, timestamp } = action.payload;
      const directory = state.directories[dirPk];
      if (directory !== undefined) {
        directory.songs = payload.songs;
        directory.isFetching = false;
        directory.invalid = false;
        directory.lastUpdated = timestamp;
        state.lastUpdated = timestamp;
      }
    },
    toggleDirectoryExpand: (state, action) => {
      const { dirPk } = action.payload;
      const directory = state.directories[dirPk];
      if (directory !== undefined) {
        directory.expanded = !directory.expanded;
      }
    },
  },
});

function fetchDirectories(userPk) {
  return api.getDirectoryList({
    userPk,
    before: directoriesSlice.actions.requestDirectories,
    failure: directoriesSlice.actions.failedFetchDirectories,
    success: directoriesSlice.actions.receiveDirectories,
  });
}


function shouldFetchDirectories(state) {
  const { directories, user } = state;
  if (user.pk !== directories.user) {
    return true;
  }
  if (directories.isFetching) {
    return false;
  }
  return directories.invalid;
}

export function fetchDirectoriesIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchDirectories(state)) {
      return dispatch(fetchDirectories(state.user.pk));
    }
    return Promise.resolve(state.directories);
  };
}

function fetchDirectoryDetail(dirPk) {
  return api.getDirectoryDetail({
    dirPk,
    before: directoriesSlice.actions.requestDirectoryDetail,
    failure: directoriesSlice.actions.failedFetchDirectoryDetail,
    success: directoriesSlice.actions.receiveDirectoryDetail,
  });
}

function shouldFetchDirectoryDetail(state, dirPk) {
  const { directories, user } = state;
  if (user.pk !== directories.user) {
    return false;
  }
  if (directories.isFetching) {
    return false;
  }
  const directory = directories.directories[dirPk];
  if (directory === undefined) {
    return false;
  }
  return (directory.invalid || directory.lastUpdated === null) && !directory.isFetching;
}

export function fetchDirectoryDetailIfNeeded(dirPk) {
  console.log(`fetchDirectoryDetailIfNeeded ${dirPk}`);
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchDirectoryDetail(state, dirPk)) {
      return dispatch(fetchDirectoryDetail(dirPk));
    }
    return Promise.resolve(state.directories.directories[dirPk]);
  };
}

userChangeListeners.receive.directories = directoriesSlice.actions.receiveUser;
userChangeListeners.login.directories = directoriesSlice.actions.receiveUser;
userChangeListeners.logout.directories = directoriesSlice.actions.logoutUser;

export const initialState = directoriesSlice.initialState;

export const { toggleDirectoryExpand } = directoriesSlice.actions;

export default directoriesSlice.reducer;
