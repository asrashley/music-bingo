import React from 'react';
import { waitFor } from '@testing-library/react';
import log from 'loglevel';

import { renderWithProviders, setFormFields } from '../../../tests';
import { RegisterForm } from './RegisterForm';

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

describe('RegisterForm component', () => {

  afterEach(() => {
    log.resetLevel();
  });

  it('registers a new user', async () => {
    const props = {
      onSubmit: vi.fn(() => Promise.resolve(true)),
      onCancel: vi.fn(),
      checkUser: vi.fn(() => Promise.resolve(true))
    };
    const newUser = {
      username: 'anewuser',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    };
    const { events, getByText } = renderWithProviders(
      <RegisterForm {...props} />);
    getByText("Register");
    //log.setLevel('debug');
    await setAddUserFields(newUser, events);
    await events.click(getByText('Register'));
    await waitFor(() => {
      log.debug(`length=${props.onSubmit.mock.calls.length}`);
      expect(props.onSubmit).toHaveBeenCalledTimes(1);
    });
    expect(props.onSubmit.mock.calls).toEqual([[{
      ...newUser,
      confirmPassword: newUser.password
    }]]);
  });

  it('refuses to register a user with a username that is too short', async () => {
    const newUser = {
      username: 'ab',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    };
    const props = {
      onSubmit: vi.fn(() => Promise.resolve(true)),
      onCancel: vi.fn(),
      checkUser: vi.fn(() => Promise.resolve(true))
    };

    const { events, getByText, findByDisplayValue } = renderWithProviders(
      <RegisterForm {...props} />);
    getByText("Register");
    await setAddUserFields(newUser, events);
    await findByDisplayValue(newUser.email);
    expect(getByText('Register')).toBeDisabled();
  });
});