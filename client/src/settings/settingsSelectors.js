import { createSelector } from 'reselect';

const getOrder = (state) => state.settings.order;
const getSettingsMap = (state) => state.settings.settings;

export const getSettingsLastUpdate = (state) => state.settings.lastUpdated;

export const getSettingsIsSaving = (state) => state.settings.isSaving;

export const getSettings = createSelector(
  [getOrder, getSettingsMap],
  (order, settingsMap) => {
    return order.map(name => settingsMap[name]);
  });
