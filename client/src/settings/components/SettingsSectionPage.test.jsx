import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders, installFetchMocks, jsonResponse, setFormFields } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { SettingsSectionPage } from './SettingsSectionPage';
import routes from '../../routes';

import settings from '../../fixtures/settings.json';
import user from '../../fixtures/userState.json';

describe('SettingsSectionPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it.each(Object.keys(settings))('to shows the settings for the "%s" section', async (section) => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const match = {
      params: {
        section
      }
    };
    const { asFragment } = renderWithProviders(<SettingsSectionPage match={match} />, { store });
    await screen.findByLabelText(settings[section][0].title);
    settings[section].forEach((setting) => {
      screen.getByLabelText(setting.title);
    });
    expect(asFragment()).toMatchSnapshot();
  });

  it('allows changes to be saved', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const match = {
      params: {
        section: 'app'
      }
    };
    fetchMock.post('/api/settings', (urls, opts) => {
      const payload = JSON.parse(opts.body);
      expect(payload).toEqual({
        app: {
          'games_dest': 'DestDirectory'
        }
      });
      return jsonResponse({
        success: true,
        changes: ['app.games_dest']
      });
    });
    const newPage = await new Promise((resolve) => {
      const history = {
        push: resolve
      };
      renderWithProviders(<SettingsSectionPage match={match} history={history} />, { store });
      screen.findByLabelText(settings.app[0].title)
        .then(() => {
          setFormFields([{
            label: 'Games Dest',
            value: 'DestDirectory'
          }]);
          fireEvent.click(screen.getByText('Save Changes'));
        });
    });
    expect(newPage).toEqual(`${routes.settingsIndex}`);
  });

  it('shows the server error message', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const match = {
      params: {
        section: 'app'
      }
    };
    fetchMock.post('/api/settings', (urls, opts) => {
      const payload = JSON.parse(opts.body);
      expect(payload).toEqual({
        app: {
          'games_dest': 'DestDirectory'
        }
      });
      return jsonResponse({
        success: false,
        error: 'an error message'
      });
    });
    renderWithProviders(<SettingsSectionPage match={match} />, { store });
    await screen.findByLabelText(settings.app[0].title);
    setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }]);
    fireEvent.click(await screen.findByText('Save Changes'));
    await screen.findByText('an error message');
  });

  it('shows error message if server is unavailable', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const match = {
      params: {
        section: 'app'
      }
    };
    fetchMock.post('/api/settings', () => 500);
    renderWithProviders(<SettingsSectionPage match={match} />, { store });
    await screen.findByLabelText(settings.app[0].title);
    setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }]);
    fireEvent.click(await screen.findByText('Save Changes'));
    await screen.findByText('500: Internal Server Error');
  });

  it('shows a message if no settings to save', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const match = {
      params: {
        section: 'app'
      }
    };
    renderWithProviders(<SettingsSectionPage match={match} />, { store });
    await screen.findByLabelText(settings.app[0].title);
    fireEvent.click(await screen.findByText('Save Changes'));
    await screen.findByText('No changes to save');
  });
});