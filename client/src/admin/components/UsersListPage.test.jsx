import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { UsersListPage } from './UsersListPage';

describe('UsersListPage component', () => {
  let apiMocks;
  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMocks = null;
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
      screen.getByText(user.email);
      if (user.username === 'admin') {
        screen.getAllByText(user.username);
      } else {
        screen.getByText(user.username);
      }
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

  it('can modify a user', async () => {
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
    const newEmail = 'a.new.email@address.test';
    fetchMock.post('/api/users', (url, opts) => {
      const body = JSON.parse(opts.body);
      expect(body.length).toEqual(1);
      const { pk, email } = body[0];
      expect(email).toEqual(newEmail);
      expect(pk).toEqual(usersListData['default'][0].pk);
      return apiMocks.jsonResponse({
        errors: [],
        added: [],
        modified: [pk],
        deleted: []
      });
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    await result.findByText(usersListData['default'][0].email);
    const firstUser = usersListData['default'][0];
    fireEvent.click(await screen.findByText(firstUser.email));
    const inputNode = await screen.findByDisplayValue(firstUser.email);
    fireEvent.input(inputNode, {
      target: {
        value: newEmail
      }
    });
    fireEvent.keyDown(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    fireEvent.keyUp(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    log.setLevel('debug');
    fireEvent.click(await screen.findByText('Save Changes'));
    await screen.findByText("Confirm save changes");
    fireEvent.click(screen.getByText('Yes Please'));
    await screen.findByText(newEmail);
    const { admin } = store.getState();
    const { users } = admin;
    for (let i = 0; i < users.length; ++i) {
      if (users[i].pk === usersListData['default'][0].pk) {
        expect(users[i].email).toEqual(newEmail);
      }
    }
  });

});