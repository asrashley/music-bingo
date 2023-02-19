import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import waitForExpect from 'wait-for-expect'
import log from 'loglevel';

import { renderWithProviders } from '../../testHelpers';
import { AddUserDialog } from './AddUserDialog';

function setAddUserFields(dest, { username, email, password }) {
  fireEvent.input(dest.getByLabelText('Username'), {
    target: {
      value: username
    }
  });
  fireEvent.input(dest.getByLabelText('Email address'), {
    target: {
      value: email
    }
  });
  fireEvent.input(dest.container.querySelector('input[name="password"]'), {
    target: {
      value: password
    }
  });
  fireEvent.input(dest.container.querySelector('input[name="confirmPassword"]'), {
    target: {
      value: password
    }
  });
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
			onAddUser: jest.fn(() => Promise.resolve(true)),
			onClose: jest.fn(),
			backdrop: false,
			users
    };

		const result = renderWithProviders(
			<AddUserDialog {...props} />);
    result.getByText("Add User");
    setAddUserFields(result, {
      username: 'newuser',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    });
    log.setLevel('trace');
    const submit = await screen.findByText('Add');
    expect(submit).not.toBeDisabled();
    fireEvent.click(submit);
    await waitForExpect(() => {
      expect(props.onAddUser).toHaveBeenCalledTimes(1);
    });
    return true;
  });

  it('refuses to add a user that already exists', async () => {
    const props = {
      onAddUser: jest.fn(() => Promise.resolve(true)),
      onClose: jest.fn(),
      backdrop: false,
      users
    };

    const result = renderWithProviders(
      <AddUserDialog {...props} />);
    result.getByText("Add User");
    log.setLevel('debug');
    setAddUserFields(result, {
      ...users[0],
      password: 'my.weak.secret'
    });
    await screen.findByDisplayValue(users[0].email);
    expect(screen.getByText('Add')).toBeDisabled();
    return true;
  });
});