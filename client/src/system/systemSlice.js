import { createSlice } from '@reduxjs/toolkit';

export const initialGitInfo = {
  branch: 'main',
  tags: '',
  commit: {
    date: '',
    hash: '',
    message: '',
    shortHash: ''
  }
};

export const initialState = {
  isFetching: false,
  isSaving: false,
  invalid: true,
  error: null,
  lastUpdated: 0,
  gitInfo: initialGitInfo,
};

export const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    invalidateSystem: state => {
      state.invalid = true;
    },
    requestSystem: state => {
      state.isFetching = true;
    },
    receiveSystem: (state, action) => {
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = Date.now();
      state.invalid = false;
      state.gitInfo = action.payload;
    },
    failedFetchSystem: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.invalid = true;
    },
  }
});

function shouldFetchSystem(state) {
  const { system } = state;
  if (system.isFetching) {
    return false;
  }
  return system.invalid;
}

function fetchGitInfo() {
  return (dispatch, getState) => {
    const infoElt = document.getElementById('buildInfo');
    if (!infoElt) {
      dispatch(systemSlice.actions.failedFetchSystem({
        error: "Failed to find build information DOM element",
        timestamp: Date.now()
      }));
      return;
    }
    try {
      const gitInfo = JSON.parse(infoElt.innerHTML);
      dispatch(systemSlice.actions.receiveSystem(gitInfo));
    } catch (err) {
      dispatch(systemSlice.actions.failedFetchSystem({
        timestamp: Date.now(),
        error: `${err.name}: ${err.message}`
      }));
    }
  };
}

export function fetchSystemIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchSystem(state)) {
      dispatch(systemSlice.actions.requestSystem());
      return dispatch(fetchGitInfo());
    }
    return Promise.resolve(false);
  };
}

export const { invalidateSystem } = systemSlice.actions;

export default systemSlice.reducer;
