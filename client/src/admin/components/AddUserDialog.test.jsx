import React from 'react';
import { waitFor } from '@testing-library/react';
import log from 'loglevel';

import { renderWithProviders, setFormFields } from '../../testHelpers';
import { AddUserDialog } from './AddUserDialog';

async function setAddUserFields({ username, email, password }, events) {
  await setFormFields([{
    label: 'Username',
    value: username,
  }, {
    label: 'Email address',
    value: email,
  }, {
    label: /^Password/,
    value: password,
  }, {
    label: 'Confirm Password',
    value: password,
    exact: false,
  }], events);
}

describe('AddUserDialog component', () => {
  const users = [];
  beforeAll(() => {
    const options = {
      "colourScheme": "cyan",
      "colourSchemes": [
        "blue",
        "christmas",
        "cyan",
        "green",
        "grey",
        "magenta",
        "orange",
        "pink",
        "pride",
        "purple",
        "red",
        "yellow"
      ],
      "maxTickets": 2,
      "rows": 3,
      "columns": 5
    };
    for (let i = 0; i < 5; ++i) {
      users.push({
        username: `user${i + 1}`,
        email: `user${i + 1}@music.bingo`,
        pk: i + 2,
        groups: {
          "users": true,
        },
        options
      });
    }
  });

  afterEach(log.resetLevel);

  it('adds a new user', async () => {
    const props = {
      onAddUser: vi.fn(() => Promise.resolve(true)),
      onClose: vi.fn(),
      backdrop: false,
      users
    };

    const { events, findByText, getByText } = renderWithProviders(
      <AddUserDialog {...props} />);
    getByText("Add User");
    await setAddUserFields({
      username: 'newuser',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    }, events);
    const submit = await findByText('Add');
    expect(submit).not.toBeDisabled();
    await events.click(submit);
    await waitFor(() => {
      expect(props.onAddUser).toHaveBeenCalledTimes(1);
    });
  });

  it('refuses to add a user that already exists', async () => {
    const props = {
      onAddUser: vi.fn(() => Promise.resolve(true)),
      onClose: vi.fn(),
      backdrop: false,
      users
    };

    const { events, findByText, findByDisplayValue, getByText } = renderWithProviders(
      <AddUserDialog {...props} />);
    getByText("Add User");
    await setAddUserFields({
      ...users[0],
      password: 'my.weak.secret'
    }, events);
    await findByDisplayValue(users[0].email);
    expect(await findByText('Add')).toBeDisabled();
  });
});
