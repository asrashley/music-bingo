import React from 'react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { UsersListPage } from './UsersListPage';

import user from '../../fixtures/userState.json';
import usersList from '../../fixtures/users.json';

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
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    await result.findByText(usersList[0].email);
    const state = store.getState();
    usersList.forEach((user, index) => {
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
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const newEmail = 'a.new.email@address.test';
    fetchMock.post('/api/users', (url, opts) => {
      const body = JSON.parse(opts.body);
      expect(body.length).toEqual(1);
      const { pk, email } = body[0];
      expect(email).toEqual(newEmail);
      expect(pk).toEqual(usersList[0].pk);
      return apiMocks.jsonResponse({
        errors: [],
        added: [],
        modified: [pk],
        deleted: []
      });
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    await result.findByText(usersList[0].email);
    const firstUser = usersList[0];
    fireEvent.click(await screen.findByText(firstUser.email));
    const inputNode = await screen.findByDisplayValue(firstUser.email);
    fireEvent.input(inputNode, {
      target: {
        value: newEmail
      }
    });
    fireEvent.keyDown(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    fireEvent.keyUp(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    fireEvent.click(await screen.findByText('Save Changes'));
    await screen.findByText("Confirm save changes");
    fireEvent.click(screen.getByText('Yes Please'));
    await screen.findByText(newEmail);
    const { admin } = store.getState();
    const { users } = admin;
    for (let i = 0; i < users.length; ++i) {
      if (users[i].pk === usersList[0].pk) {
        expect(users[i].email).toEqual(newEmail);
      }
    }
  });

  it('can delete a user', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const fetchPromise = new Promise((resolve) => {
      fetchMock.post('/api/users', (url, opts) => {
        const body = JSON.parse(opts.body);
        expect(body.length).toEqual(1);
        const { pk, deleted } = body[0];
        expect(deleted).toEqual(true);
        expect(pk).toEqual(usersList[0].pk);
        resolve(body);
        return apiMocks.jsonResponse({
          errors: [],
          added: [],
          modified: [],
          deleted: [pk]
        });
      });
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    await result.findByText(usersList[0].email);
    const firstUser = usersList[0];
    let emailCell = await screen.findByText(firstUser.email);
    let row = emailCell.parentElement;
    while (!row.classList.contains('rs-table-row')) {
      row = row.parentElement;
    }
    fireEvent.click(row.querySelector('input[type="checkbox"]'));
    fireEvent.click(await screen.findByText('Delete'));
    emailCell = await screen.findByText(firstUser.email);
    expect(emailCell).toHaveClass('deleted');
    expect(emailCell).toHaveClass('modified');
    fireEvent.click(screen.getByText('Save Changes'));
    fireEvent.click(await screen.findByText('Yes Please'));
    await fetchPromise;
  });

});