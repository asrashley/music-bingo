import React from 'react';
import log from 'loglevel';
import { screen, waitFor } from '@testing-library/react';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';
import { createMemoryHistory } from 'history';
import fetchMock from 'fetch-mock';

import {
  renderWithProviders,
  installFetchMocks,
  jsonResponse,
  setFormFields
} from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { SettingsSectionPage } from './SettingsSectionPage';
import { routes } from '../../routes';
import { Outlet, Route, Routes } from 'react-router-dom';

import settings from '../../../tests/fixtures/settings.json';
import { adminUser } from '../../../tests/MockServer';

function TestSettingsSectionPage() {
  return (
    <Routes>
      <Route path="/" element={<div>Index page</div>} />
      <Route path="/user/settings" element={<Outlet />}>
        <Route path="" element={<div>SettingsIndexPage</div>} />
        <Route path=":section" element={<SettingsSectionPage />} />
      </Route>
    </Routes>
  );
}

describe('SettingsSectionPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation((url) => ({
    type: 'change-location',
    payload: {
      url,
    },
  }));
  let apiMock, user;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
    user = apiMock.getUserState(adminUser);
  });

  afterEach(() => {
    apiMock.shutdown();
    fetchMock.reset();
    pushSpy.mockClear();
    log.resetLevel();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it.each(Object.keys(settings))('to shows the settings for the "%s" section', async (section) => {
    const history = createMemoryHistory({
      initialEntries: ['/', `/user/settings/${section}`],
      initialIndex: 1,
    });
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
    const { asFragment, findByLabelText } = renderWithProviders(
      <TestSettingsSectionPage />, { history, store });
    await findByLabelText(settings[section][0].title);
    settings[section].forEach((setting) => {
      screen.getByLabelText(setting.title);
    });
    expect(asFragment()).toMatchSnapshot();
  });

  it('allows changes to be saved', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', '/user/settings/app'],
      initialIndex: 1,
    });
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
    const { events, findByLabelText, getByText } = renderWithProviders(
      <TestSettingsSectionPage />, { history, store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await events.click(getByText('Save Changes'));
    const { body } = fetchMock.lastCall('/api/settings', 'POST')[1];
    expect(JSON.parse(body)).toEqual({
      app: {
        'games_dest': 'DestDirectory'
      }
    });
    await expect(newPage).resolves.toEqual(`${routes.settingsIndex}`);
  });

  it('shows the server error message', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', '/user/settings/app'],
      initialIndex: 1,
    });
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
    apiMock.setResponseModifier('/api/settings', 'POST', (_url, opts) => {
      expect(opts.json).toEqual({
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
      <TestSettingsSectionPage />, { history, store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await waitFor(async () => {
      await events.click(await screen.findByText('Save Changes'));
    });
    await findByText('an error message');
  });

  it('shows error message if server is unavailable', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', '/user/settings/app'],
      initialIndex: 1,
    });
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
    apiMock.setResponseModifier('/api/settings', 'POST', () => 500);
    const { events, findByLabelText, findByText } = renderWithProviders(
      <TestSettingsSectionPage />, { history, store });
    await findByLabelText(settings.app[0].title);
    await setFormFields([{
      label: 'Games Dest',
      value: 'DestDirectory'
    }], events);
    await waitFor(async () => {
      await events.click(await screen.findByText('Save Changes'));
    });
    await findByText('500: Internal Server Error');
  });

  it('shows a message if no settings to save', async () => {
    const history = createMemoryHistory({
      initialEntries: ['/', '/user/settings/app'],
      initialIndex: 1,
    });
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
    const { events, findByLabelText, findByText } = renderWithProviders(
      <TestSettingsSectionPage />, { history, store });
    await findByLabelText(settings.app[0].title);
    await events.click(await screen.findByText('Save Changes'));
    await findByText('No changes to save');
  });
});