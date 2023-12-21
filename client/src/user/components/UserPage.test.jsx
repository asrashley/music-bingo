import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { UserPage, UserPageComponent } from './UserPage';
import { userSlice } from '../userSlice';
import * as user from '../../fixtures/userState.json';

describe('UserPage component', () => {
  let apiMocks;

  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    jest.clearAllMocks();
    log.resetLevel();
    apiMocks = null;
    log.resetLevel();
  });

  afterAll(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  it('renders without throwing an exception with initial state', () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      user: initialState.user
    };
    const result = renderWithProviders(<UserPageComponent {...props} />);
    result.getByText('Log out');
  });

  it.only('updates settings once user has logged in', async () => {
    const username = 'my.username';
    const password = 'password!';
    const store = createStore(initialState);
    const history = {
      push: jest.fn(),
    };
    apiMocks.addUser({
      username,
      password,
      groups: ['users'],
      pk: 12,
    });
    const { getByText } = renderWithProviders(<UserPage history={history} />, { store });
    getByText('Log out');

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

    await screen.findByText('my.username');
  });

  it('renders admin user actions', async () => {
    const store = createStore({
      ...initialState,
      user
    });
    const history = {
      push: jest.fn()
    };
    const { asFragment } = renderWithProviders(<UserPage history={history} />, { store });
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
    await Promise.all(actions.map(item => screen.findByText(item)));
    expect(asFragment()).toMatchSnapshot();
  });
});
