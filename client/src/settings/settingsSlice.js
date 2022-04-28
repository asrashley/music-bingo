import { createSlice } from '@reduxjs/toolkit';

import { api } from '../endpoints';
import { userChangeListeners } from '../user/userSlice';

export const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    settings: {},
    order: [],
    isFetching: false,
    isSaving: false,
    invalid: true,
    error: null,
    lastUpdated: 0,
    user: -1,
  },
  reducers: {
    receiveUser: (state, action) => {
      const user = action.payload.payload;
      if (user.pk !== state.pk) {
        state.user = user.pk;
        if (state.isFetching === false) {
          state.settings = {};
          state.order = [];
          state.invalid = true;
        }
      }
    },
    logoutUser: (state) => {
      state.user = -1;
      state.settings = {};
      state.order = [];
      state.invalid = true;
    },
    invalidateSettings: state => {
      state.invalid = true;
    },
    requestSettings: state => {
      state.isFetching = true;
    },
    receiveSettings: (state, action) => {
      const { timestamp, payload } = action.payload;
      const order = [];
      const settings = {};
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.invalid = false;
      payload.forEach((field) => {
        order.push(field.name);
        settings[field.name] = field;
      });
      state.settings = settings;
      state.order = order;
    },
    failedFetchSettings: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.invalid = true;
    },
    modifySetting: (state, action) => {
      const { field, value } = action.payload;
      state.settings[field] = {
          ...state.settings[field],
        [field]: value,
        modified: true,
      };
    },
    bulkModifySettings: (state, action) => {
      const changes = action.payload;
      changes.forEach(({field, value}) => {
        state.settings[field] = {
          ...state.settings[field],
          value,
          modified: true
        };
      });
    },
    savingModifiedSettings: (state, action) => {
      state.isSaving = true;
    },
    failedSaveModifiedSettings: (state, action) => {
      const { error } = action.payload;
      state.isSaving = false;
      state.error = error;
    },
    saveModifiedSettingsDone: (state, action) => {
      const { timestamp } = action.payload;
      const newSettings = {};
      for (const [key, field] of Object.entries(state.settings)) {
        newSettings[key] = {
          ...field,
          modified: false
        };
      }
      state.isSaving = false;
      state.lastUpdated = timestamp;
      state.settings = newSettings;
    },
  }
});

function fetchSettings(userId) {
  return api.getSettings({
    before: settingsSlice.actions.requestSettings,
    success: settingsSlice.actions.receiveSettings,
    failure: settingsSlice.actions.failedFetchSettings,
  });
}

function shouldFetchSettings(state) {
  const { settings, user } = state;
  if (settings.isFetching || settings.isSaving || user.pk < 0) {
    return false;
  }
  return settings.invalid || user.pk !== settings.user;
}

export function fetchSettingsIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchSettings(state)) {
      return dispatch(fetchSettings(state.user.pk));
    }
    return Promise.resolve();
  };
}

export function saveModifiedSettings() {
  return (dispatch, getState) => {
    const {settings} = getState();
    const changes = {};
    let modified = false;
    for (const [key, field] of Object.entries(settings.settings)) {
      //console.log(`${key}: ${field.modified}`);
      if (field.modified === true) {
        changes[key] = field.value;
        modified = true;
      }
    }
    console.dir(changes);
    if (!modified) {
      return Promise.resolve({});
    }
    return dispatch(api.modifySettings({
      body: changes,
      before: settingsSlice.actions.savingModifiedSettings,
      success: settingsSlice.actions.saveModifiedSettingsDone,
      failure: settingsSlice.actions.failedSaveModifiedSettings,
    }));
  };
}


export const { invalidateSettings, modifySetting,
               bulkModifySettings } = settingsSlice.actions;
userChangeListeners.receive.settings = settingsSlice.actions.receiveUser;
userChangeListeners.login.settings = settingsSlice.actions.receiveUser;
userChangeListeners.logout.settings = settingsSlice.actions.logoutUser;

export const initialState = settingsSlice.initialState;

export default settingsSlice.reducer;
