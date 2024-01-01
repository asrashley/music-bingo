/* global __BUILD_INFO__ */

import { createSlice } from '@reduxjs/toolkit';

export const initialBuildInfo = {
  branch: 'main',
  tags: '',
  version: '0.0.0',
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
  buildInfo: {
    ...initialBuildInfo,
  },
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
      state.buildInfo = action.payload;
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

function fetchBuildInfo() {
  return (dispatch) => {
    dispatch(systemSlice.actions.receiveSystem(__BUILD_INFO__));
  };
}

export function fetchSystemIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchSystem(state)) {
      dispatch(systemSlice.actions.requestSystem());
      return dispatch(fetchBuildInfo());
    }
    return Promise.resolve(false);
  };
}

export const { invalidateSystem } = systemSlice.actions;

export default systemSlice.reducer;
