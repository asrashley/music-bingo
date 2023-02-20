import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { UsersListPage } from './UsersListPage';

describe('UsersListPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to shows a list of users', async () => {
    const [userData, usersListData] = await Promise.all([
      import('../../fixtures/userState.json'),
      import('../../fixtures/users.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    await result.findByText(usersListData['default'][0].email);
    const state = store.getState();
    usersListData['default'].forEach((user, index) => {
      result.findByText(user.email);
      result.findByText(user.username);
      const groups = {};
      user.groups.forEach(g => groups[g] = true);
      const expected = {
        ...user,
        modified: false,
        deleted: false,
        password: '',
        groups
      };
      expect(state.admin.users[index]).toEqual(expected);
    });
    expect(result.asFragment()).toMatchSnapshot();
  });

});