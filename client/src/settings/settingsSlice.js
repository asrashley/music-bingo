import { createSlice } from '@reduxjs/toolkit';

import { api } from '../endpoints';
import { userChangeListeners } from '../user/userSlice';

export const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    sections: {},
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
          state.sections = {};
          state.invalid = true;
        }
      }
    },
    logoutUser: (state) => {
      state.user = -1;
      state.sections = {};
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
      state.isFetching = false;
      state.error = null;
      state.lastUpdated = timestamp;
      state.invalid = false;
      state.sections = {};
      for (let section in payload) {
        const order = [];
        const settings = {};
        payload[section].forEach((field) => {
          order.push(field.name);
          settings[field.name] = field;
        });
        state.sections[section] = {
          settings,
          order,
          valid: true
        };
      }
    },
    failedFetchSettings: (state, action) => {
      const { timestamp, error } = action.payload;
      state.isFetching = false;
      state.lastUpdated = timestamp;
      state.error = error;
      state.invalid = true;
      state.sections = {};
    },
    modifySetting: (state, action) => {
      const { section, field, value } = action.payload;
      state.sections[section].settings[field] = {
        ...state.sections[section].settings[field],
        [field]: value,
        modified: true,
      };
    },
    bulkModifySettings: (state, action) => {
      const changes = action.payload;
      changes.forEach(({ section, field, value }) => {
        if (state.sections[section] !== undefined) {
          state.sections[section].settings[field].value = value;
          state.sections[section].settings[field].modified = true;
        }
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
      Object.values(state.sections).forEach((sectionObj) => {
        for (const key in sectionObj.settings) {
          sectionObj.settings[key].modified = false;
        }
      });
      state.isSaving = false;
      state.lastUpdated = timestamp;
    },
  }
});

function fetchSettings() {
  return api.getSettings({
    before: settingsSlice.actions.requestSettings,
    success: settingsSlice.actions.receiveSettings,
    failure: settingsSlice.actions.failedFetchSettings,
  });
}

function shouldFetchSettings(state) {
  const { settings, user } = state;
  if (settings.isFetching || settings.isSaving) {
    return false;
  }
  return settings.invalid || user.pk !== settings.user;
}

export function fetchSettingsIfNeeded() {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchSettings(state)) {
      return dispatch(fetchSettings());
    }
    return Promise.resolve();
  };
}

export function saveModifiedSettings() {
  return (dispatch, getState) => {
    const { settings } = getState();
    const { sections } = settings;
    const changes = {};
    let modified = false;
    for (const [sectionName, sectionObj] of Object.entries(sections)) {
      for (const [key, field] of Object.entries(sectionObj.settings)) {
        if (field.modified === true) {
          if (changes[sectionName] === undefined) {
            changes[sectionName] = {};
          }
          changes[sectionName][key] = field.value;
          modified = true;
        }
      }
    }
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
