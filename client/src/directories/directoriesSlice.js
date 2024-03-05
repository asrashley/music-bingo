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

export const initialState = {
  directories: {},
  user: -1,
  isFetching: false,
  didInvalidate: false,
  error: null,
  lastUpdated: null,
  invalid: true,
  displayOptions: {
    ascending: true,
    field: 'title',
    onlyExisting: true,
  },
  query: {
    dirPk: undefined,
    searching: false,
    query: '',
    results: [],
    resultMap: null,
    lastUpdated: -1
  }
};

export const directoriesSlice = createSlice({
  name: 'directories',
  initialState,
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.user && state.isFetching === false) {
        state.directories = {};
        state.user = user.pk;
      }
    },
    logoutUser: (state) => {
      state.games = {};
      state.Directories = {};
      state.user = -1;
    },
    requestDirectories: (state) => {
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
    requestSearchSongs: (state, action) => {
      const { query, dirPk } = action.payload;
      state.query = {
        searching: true,
        query,
        dirPk,
        results: [],
        resultMap: null,
        lastUpdated: Date.now()
      };
    },
    failedSearchSongs: (state, action) => {
      const { dirPk, query } = action.payload;
      if (query === state.query.query && dirPk === state.query.dirPk) {
        state.query.searching = false;
      }
    },
    receiveSearchSongs: (state, action) => {
      const { dirPk, query, payload, timestamp } = action.payload;
      if (query === state.query.query && dirPk === state.query.dirPk) {
        state.query.searching = false;
        state.query.results = payload;
        state.query.resultMap = {};
        payload.forEach(song => state.query.resultMap[song.pk] = song);
        state.lastUpdated = state.query.lastUpdated = timestamp;
      }
    },
    clearSeachResults: (state) => {
      state.query = {
        searching: false,
        query: '',
        results: [],
        resultMap: null,
        dirPk: undefined,
        lastUpdated: -1
      };
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
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchDirectoryDetail(state, dirPk)) {
      return dispatch(fetchDirectoryDetail(dirPk));
    }
    return Promise.resolve(state.directories.directories[dirPk]);
  };
}

export function searchForSongs(query, dirPk) {
  return (dispatch, getState) => {
    const { directories } = getState();
    if (dirPk !== undefined && directories.directories[dirPk].expaned === true) {
      const queryText = query.toLowerCase();
      const songs = directories.directories[dirPk].songs.filter((song) => {
        if (typeof (song) !== 'object') {
          return false;
        }
        return song.title.toLowerCase().indexOf(queryText) > -1;
      });
      dispatch(directoriesSlice.actions.requestSearchSongs({
        dirPk,
        query,
      }));
      return dispatch(directoriesSlice.actions.receiveSearchSongs({
        dirPk,
        query,
        payload: songs,
        timestamp: Date.now()
      }));
    }
    return dispatch(api.searchForSongs({
      dirPk,
      query,
      before: directoriesSlice.actions.requestSearchSongs,
      failure: directoriesSlice.actions.failedSearchSongs,
      success: directoriesSlice.actions.receiveSearchSongs,
    }));
  };
}

userChangeListeners.receive.directories = directoriesSlice.actions.receiveUser;
userChangeListeners.login.directories = directoriesSlice.actions.receiveUser;
userChangeListeners.logout.directories = directoriesSlice.actions.logoutUser;

export const { clearSeachResults, toggleDirectoryExpand } = directoriesSlice.actions;

export default directoriesSlice.reducer;
