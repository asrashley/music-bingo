import React from 'react';

import { renderWithProviders, fetchMock, installFetchMocks, } from '../../../tests';
import { SettingsIndexPage } from './SettingsIndexPage';
import user from '../../../tests/fixtures/userState.json';
import { initialState, createStore } from '../../store';
import log from 'loglevel';

describe('SettingsIndexPage component', () => {
  const settingsSections = ['app', 'database', 'privacy', 'smtp'];
  let apiMock;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    apiMock = null;
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
        accessToken: apiMock.getAccessToken(),
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
    log.setLevel('debug');
    const { findByText, asFragment } = renderWithProviders(<SettingsIndexPage />, { store });
    await Promise.all(settingsSections.map(async (section) => {
      const link = await findByText(`Modify ${section} Settings`);
      expect(link.href).toMatch(new RegExp(`/user/settings/${section}$`));
    }));
    expect(asFragment()).toMatchSnapshot();
  });
});


