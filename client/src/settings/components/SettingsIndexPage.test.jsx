import React from 'react';
import fetchMock from 'fetch-mock';

import { renderWithProviders } from '../../../tests';
import { MockBingoServer, adminUser, normalUser } from '../../../tests/MockServer';
import { SettingsIndexPage } from './SettingsIndexPage';
import { initialState, createStore } from '../../store';

describe('SettingsIndexPage component', () => {
  const settingsSections = ['app', 'database', 'privacy', 'smtp'];
  let apiMock;

  beforeEach(() => {
    apiMock = new MockBingoServer(fetchMock);
  });

  afterEach(() => {
    apiMock = null;
    fetchMock.reset();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('only an Admin can modify settings', async () => {
    const store = createStore({
      ...initialState,
      user: apiMock.getUserState(normalUser),
    });
    const { getByText, queryByText } = renderWithProviders(<SettingsIndexPage />, { store });
    getByText('Only an admin can modify settings');
    settingsSections.forEach(section =>
      expect(queryByText(section, { exact: false })).toBeNull());
  });

  it('shows link to each settings section', async () => {
    const store = createStore({
      ...initialState,
      user: apiMock.getUserState(adminUser),
    });
    const { findByText, asFragment } = renderWithProviders(<SettingsIndexPage />, { store });
    await Promise.all(settingsSections.map(async (section) => {
      const link = await findByText(`Modify ${section} Settings`);
      expect(link.href).toMatch(new RegExp(`/user/settings/${section}$`));
    }));
    expect(asFragment()).toMatchSnapshot();
  });
});
