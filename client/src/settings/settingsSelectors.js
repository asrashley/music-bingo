import { createSelector } from 'reselect';

export const getCurrentSection = (state, props) => props.match?.params.section;
const getAllSections = (state, props) => state.settings.sections;

export const getSettingsLastUpdate = (state) => state.settings.lastUpdated;
export const getSettingsIsSaving = (state) => state.settings.isSaving;

const getCurrentSettingsSection = createSelector(
  [getCurrentSection, getAllSections],
  (currentSection, sections) => sections[currentSection]);

export const getSettingsSections = createSelector(
  [getAllSections],
  (sections) => Object.keys(sections).sort());

export const getSettings = createSelector(
  [getCurrentSettingsSection],
  (section) => {
    if (section === undefined) {
      return [];
    }
    return section.order.map(name => section.settings[name]);
  });

export const getPrivacySettings = createSelector(
  [getAllSections],
  (sections) => {
    if (sections.privacy === undefined) {
      return {
        valid: false,
        name: '',
        email: '',
        address: '',
        data_center: '',
        ico: ''
      };
    }
    return {
      ...sections.privacy.settings,
      valid: sections.privacy.valid
    };
  });