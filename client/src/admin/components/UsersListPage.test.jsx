import React from 'react';
import log from 'loglevel';
import { fireEvent, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';

import { renderWithProviders, installFetchMocks } from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { UsersListPage } from './UsersListPage';

import user from '../../../tests/fixtures/userState.json';
import usersList from '../../../tests/fixtures/users.json';

async function findUserRow(result, email) {
  const emailCell = await result.findByText(email);
  let row = emailCell.parentElement;
  while (!row.classList.contains('rs-table-row')) {
    row = row.parentElement;
  }
  return row;
}

describe('UsersListPage component', () => {
  let apiMock;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    apiMock.shutdown();
    fetchMock.reset();
    log.resetLevel();
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
    const { asFragment, findByText, getByText, getAllByText } = renderWithProviders(
      <UsersListPage />, { store });

    await findByText(usersList[0].email);
    const state = store.getState();
    usersList.forEach((user, index) => {
      getByText(user.email);
      if (user.username === 'admin') {
        getAllByText(user.username);
      } else {
        getByText(user.username);
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
    expect(asFragment()).toMatchSnapshot();
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
    const { events, findByDisplayValue, findByText, getByText } = renderWithProviders(
      <UsersListPage />, { store });
    await findByText(usersList[0].email);
    const firstUser = usersList[0];
    await events.click(await findByText(firstUser.email));
    const inputNode = await findByDisplayValue(firstUser.email);
    fireEvent.input(inputNode, {
      target: {
        value: newEmail
      }
    });
    fireEvent.keyDown(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    fireEvent.keyUp(inputNode, { key: 'Enter', code: 'Enter', charCode: 13 })
    await events.click(await findByText('Save Changes'));
    await findByText("Confirm save changes");
    await events.click(getByText('Yes Please'));
    await findByText(newEmail);
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
    const fetchPromise = apiMock.addResponsePromise('/api/users', 'POST');
    const result = renderWithProviders(<UsersListPage />, { store });
    const { events, findByText, getByText } = result;
    await findByText(usersList[0].email);
    const firstUser = usersList[0];
    const row = await findUserRow(result, firstUser.email);
    await events.click(row.querySelector('input[type="checkbox"]'));
    await events.click(await findByText('Delete'));
    const emailCell = await findByText(firstUser.email);
    expect(emailCell).toHaveClass('deleted');
    expect(emailCell).toHaveClass('modified');
    await events.click(getByText('Save Changes'));
    await events.click(await findByText('Yes Please'));
    await waitFor(async () => {
      await fetchPromise;
    });
    await fetchMock.flush(true);
  });

  it('can undelete a user', async () => {
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: user.pk
      },
      user
    });
    const result = renderWithProviders(<UsersListPage />, { store });
    const { events, findByText } = result;
    await findByText(usersList[0].email);
    const firstUser = usersList[0];
    let row = await findUserRow(result, firstUser.email);
    await events.click(row.querySelector('input[type="checkbox"]'));
    await events.click(await findByText('Delete'));
    let emailCell = await findByText(firstUser.email);
    expect(emailCell).toHaveClass('deleted');
    row = await findUserRow(result, firstUser.email);
    await events.click(row.querySelector('input[type="checkbox"]'));
    await events.click(await findByText('Undelete'));
    emailCell = await findByText(firstUser.email);
    expect(emailCell).not.toHaveClass('deleted');
  });

});