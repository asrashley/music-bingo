import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { screen } from '@testing-library/react';


import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { SettingsSectionPage } from './SettingsSectionPage';

describe('SettingsSectionPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to shows the settings for the "app" section', async () => {
    const [userData, settingsData] = await Promise.all([
      import('../../fixtures/userState.json'),
      import('../../fixtures/settings.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const match = {
      params: {
        section: 'app'
      }
    };
    const { asFragment } = renderWithProviders(<SettingsSectionPage match={match} />, { store });
    await screen.findByLabelText(settingsData.app[0].title);
    settingsData.app.forEach((setting) => {
      screen.getByLabelText(setting.title);
    });
    expect(asFragment()).toMatchSnapshot();
  });

});