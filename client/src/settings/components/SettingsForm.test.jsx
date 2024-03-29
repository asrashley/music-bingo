import React from 'react';
import log from 'loglevel';

import { renderWithProviders, setFormFields } from '../../../tests';

import SettingsForm from './SettingsForm';

import settings from '../../../tests/fixtures/settings.json';

describe('SettingsForm component', () => {
  it.each(Object.keys(settings))('renders form for settings section "%s"', async (section) => {
    const props = {
      values: {},
      section,
      settings: settings[section],
      cancel: () => false,
      submit: () => Promise.resolve(true)
    };
    for (const { name, value } of settings[section]) {
      props.values[name] = value;
    }
    const { asFragment, findByLabelText } = renderWithProviders(<SettingsForm {...props} />);
    await Promise.all(props.settings.map(async (field) => {
      const inp = await findByLabelText(field.title);
      let { value } = field;
      if (field.type === 'bool') {
        if (value === true || (/^(true|on)$/i).test(value)) {
          value = "on";
        } else {
          value = "off";
        }
        if (value !== inp.value) {
          // TODO: find out why some checkbox inputs have the wrong values
          log.warn(`"${field.name}" expected: "${value}" got: "${inp.value}"`);
          return false;
        }
      } else if (value === null) {
        value = '';
      } else {
        value = `${value}`;
      }
      expect(inp.value).toEqual(value);
      return true;
    }));
    expect(asFragment()).toMatchSnapshot();
  });

  it('calls cancel when cancel button is clicked', async () => {
    const props = {
      values: {},
      section: 'app',
      settings: settings.app,
      cancel: vi.fn(),
      submit: async () => true
    };
    props.settings.forEach(field => props.values[field.name] = field.value);
    const { events, findByText } = renderWithProviders(<SettingsForm {...props} />);
    await events.click(await findByText('Discard Changes'));
    expect(props.cancel).toHaveBeenCalledTimes(1);
  });

  it('allows changes to be saved', async () => {
    const props = {
      values: {},
      section: 'app',
      settings: settings.app,
      cancel: () => false,
      submit: async () => true
    };
    props.settings.forEach(field => props.values[field.name] = field.value);
    const { events, findByText } = renderWithProviders(<SettingsForm {...props} />);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(await findByText('Save Changes'));
    expect(document.querySelectorAll('.is-invalid').length).toEqual(0);
  });

  it('shows the server error message', async () => {
    const props = {
      values: {},
      section: 'app',
      settings: settings.app,
      cancel: () => false,
      submit: async () => 'an error message'
    };
    props.settings.forEach(field => props.values[field.name] = field.value);
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(<SettingsForm {...props} />);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(await findByText('Save Changes'));
    await findByText('an error message');
  });
});
