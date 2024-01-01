import React from 'react';

import { renderWithProviders, fetchMock, installFetchMocks, } from '../../testHelpers';
import { SettingsIndexPage } from './SettingsIndexPage';
import user from '../../fixtures/userState.json';
import { initialState, createStore } from '../../store';

describe('SettingsIndexPage component', () => {
  const settingsSections = ['app', 'database', 'privacy', 'smtp'];

  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('only an Admin can modify settings', async () => {
    const store = createStore({
      ...initialState,
      user: {
        ...user,
        groups: {
          users: true,
        }
      }
    });
    const { getByText, queryByText } = renderWithProviders(<SettingsIndexPage />, { store });
    getByText('Only an admin can modify settings');
    settingsSections.forEach(section =>
      expect(queryByText(section, { exact: false })).toBeNull());
  });

  it('shows link to each settings section', async () => {
    const store = createStore({
      ...initialState,
      user,
    });
    const { findByText, asFragment } = renderWithProviders(<SettingsIndexPage />, { store });
    await Promise.all(settingsSections.map(async (section) => {
      const link = await findByText(`Modify ${section} Settings`);
      expect(link.href).toMatch(new RegExp(`/user/settings/${section}$`));
    }));
    expect(asFragment()).toMatchSnapshot();
  });
});


