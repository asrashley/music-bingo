import React from 'react';
import { getByText } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { SettingsIndexPageComponent } from './SettingsIndexPage';

describe('SettingsIndexPage component', () => {
  it('only an Admin can modify settings', async () => {
    const userData = await import('../../fixtures/user.json');
    userData["default"].groups = { "users": true };
    const props = {
      dispatch: () => false,
      settingsSections: ['app', 'database', 'privacy', 'smtp'],
      user: userData['default'],
    };
    const result = renderWithProviders(<SettingsIndexPageComponent {...props} />);
    result.getByText('Only an admin can modify settings');
    props.settingsSections.forEach(section =>
      expect(result.queryByText(section, { exact: false })).toBeNull());
  })

  it('shows each settings section', async () => {
    const userData = await import('../../fixtures/user.json');
    userData["default"].groups = {
      users: true,
      creators: true,
      hosts: true,
      admin: true
    };
    const actions = [];
    const props = {
      dispatch: (action) => actions.push(action),
      settingsSections: ['app', 'database', 'privacy', 'smtp'],
      user: userData['default'],
    };
    const result = renderWithProviders(<SettingsIndexPageComponent {...props} />);
    props.settingsSections.forEach(section => {
      const link = result.getByText(`Modify ${section} Settings`);
      expect(link.href).toEqual(`http://localhost/user/settings/${section}`);
    });
    expect(result.asFragment()).toMatchSnapshot();
  });
});


