import React from 'react';
import { act } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from 'fetch-mock';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks } from '../../../tests';
import { UserPage } from './UserPage';
import { userSlice } from '../userSlice';
import * as user from '../../../tests/fixtures/userState.json';

describe('UserPage component', () => {
  let apiMocks;

  beforeAll(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.reset();
    vi.clearAllMocks();
    log.resetLevel();
    apiMocks = null;
    log.resetLevel();
  });

  afterAll(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('renders without throwing an exception with initial state', () => {
    const { getByText } = renderWithProviders(<UserPage />);
    getByText('Log out');
  });

  it('updates settings once user has logged in', async () => {
    fetchMock.reset();
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
    const username = 'my.username';
    const password = 'password!';
    const store = createStore(initialState);
    apiMocks.addUser({
      username,
      password,
      groups: ['users'],
      pk: 12,
    });
    const { getByText, findByText } = renderWithProviders(<UserPage />, { store });
    getByText('Log out');

    await act(() => {
      store.dispatch(userSlice.actions.receiveUser({
        timestamp: 123,
        payload: {
          username: 'my.username',
          email: 'a.user',
          groups: ['users'],
          pk: 12,
          options: user.options,
        },
      }));
    });

    await findByText('my.username');
  });

  it('renders admin user actions', async () => {
    const store = createStore({
      ...initialState,
      user
    });
    const { asFragment, findByText } = renderWithProviders(<UserPage />, { store });
    const actions = [
      'Modify Users',
      'Modify Settings',
      'Guest links',
      'Import Game',
      'Import Database',
      'Export Database',
      'Change password or email address',
      'Log out'
    ];
    await Promise.all(actions.map(item => findByText(item)));
    expect(asFragment()).toMatchSnapshot();
  });
});
