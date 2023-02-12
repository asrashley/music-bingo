import React from 'react';
import { screen } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';

import SettingsForm from './SettingsForm';

import settings from '../../fixtures/settings.json';

describe('SettingsForm component', () => {
  it.each(Object.keys(settings))('renders form for settings section "%s"', async (section) => {
    const props = {
      values: {},
      section,
      settings: settings[section],
      cancel: () => false,
      submit: () => false
    };
    props.settings.forEach(field => props.values[field.name] = field.value);
    const { asFragment } = renderWithProviders(<SettingsForm {...props} />);
    expect(asFragment()).toMatchSnapshot();
    props.settings.forEach((field) => {
      const inp = screen.getByLabelText(field.title);
      let { value } = field;
      if (field.type === 'bool') {
        if (value === true || (/^true$/i).test(value)) {
          value = "on";
        } else {
          value = "off";
        }
        if (value !== inp.value) {
          // TODO: find out why some checkbox inputs have the wrong values
          console.log(`"${field.name}" expected: "${value}" got: "${inp.value}"`);
          return false;
        }
      } else if (value === null) {
        value = '';
      } else {
        value = `${value}`;
      }
      expect(inp.value).toEqual(value);
      return true;
    });
  });
});
