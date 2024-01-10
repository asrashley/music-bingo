import React from 'react';
import log from 'loglevel';
import { screen } from '@testing-library/react';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import {
  fetchMock,
  renderWithProviders,
  installFetchMocks,
  jsonResponse,
  setFormFields
} from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { SettingsSectionPage } from './SettingsSectionPage';
import { routes } from '../../routes';

import settings from '../../../tests/fixtures/settings.json';
import user from '../../../tests/fixtures/userState.json';

describe('SettingsSectionPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation((url) => ({
    type: 'change-location',
    payload: {
      url,
    },
  }));

  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    pushSpy.mockClear();
    log.resetLevel();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it.each(Object.keys(settings))('to shows the settings for the "%s" section', async (section) => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user,
      routes: {
        params: {
          section
        }
      },
    });
    const { asFragment, findByLabelText } = renderWithProviders(<SettingsSectionPage />, { store });
    await findByLabelText(settings[section][0].title);
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
      routes: {
        params: {
          section: 'app'
        }
      },
      user
    });
    let payload;
    fetchMock.post('/api/settings', (_url, opts) => {
      payload = JSON.parse(opts.body);
      //console.dir(payload);
      return jsonResponse({
        success: true,
        changes: ['app.games_dest']
      });
    });
    const newPage = new Promise((resolve) => {
      pushSpy.mockImplementationOnce((url) => {
        resolve(url);
        return {
          type: 'change-location',
          payload: {
            url
          },
        };
      });
    });
    const { events, findByLabelText, getByText } = renderWithProviders(<SettingsSectionPage />, { store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(getByText('Save Changes'));
    expect(payload).toEqual({
      app: {
        'games_dest': 'DestDirectory'
      }
    });
    await expect(newPage).resolves.toEqual(`${routes.settingsIndex}`);
  });

  it('shows the server error message', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          section: 'app'
        }
      },
      user
    });
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
    const { events, findByLabelText, findByText } = renderWithProviders(
      <SettingsSectionPage />, { store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(await screen.findByText('Save Changes'));
    await findByText('an error message');
  });

  it('shows error message if server is unavailable', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          section: 'app'
        }
      },
      user
    });
    fetchMock.post('/api/settings', () => 500);
    const { events, findByLabelText, findByText } = renderWithProviders(<SettingsSectionPage />, { store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(await screen.findByText('Save Changes'));
    await findByText('500: Internal Server Error');
  });

  it('shows a message if no settings to save', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      routes: {
        params: {
          section: 'app'
        }
      },
      user
    });
    const { events, findByLabelText, findByText } = renderWithProviders(<SettingsSectionPage />, { store });
    await findByLabelText(settings.app[0].title);
    await events.click(await screen.findByText('Save Changes'));
    await findByText('No changes to save');
  });
});