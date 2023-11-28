import React from 'react';
import { screen } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { UserPage, UserPageComponent } from './UserPage';
import * as user from '../../fixtures/userState.json';

describe('UserPage component', () => {
  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  afterAll(() => jest.useRealTimers());

  it('renders without throwing an exception with initial state', () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      user: initialState.user
    };
    installFetchMocks(fetchMock, { loggedIn: false });
    const result = renderWithProviders(<UserPageComponent {...props} />);
    result.getByText('Log out');
  });

  it('renders admin user actions', async () => {
    const store = createStore({
      ...initialState,
      user
    });
    const history = {
      push: jest.fn()
    };
    installFetchMocks(fetchMock, { loggedIn: true });
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
