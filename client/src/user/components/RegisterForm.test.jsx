import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';

import { renderWithProviders } from '../../testHelpers';
import { RegisterForm } from './RegisterForm';

async function setAddUserFields(dest, { username, email, password }) {
  fireEvent.input(screen.getByLabelText('Username'), {
    target: {
      value: username
    }
  });

  fireEvent.input(screen.getByLabelText('Email address'), {
    target: {
      value: email
    }
  });

  fireEvent.input(document.querySelector('input[name="password"]'), {
    target: {
      value: password
    }
  });

  fireEvent.input(document.querySelector('input[name="confirmPassword"]'), {
    target: {
      value: password
    }
  });
  log.debug('wait for confirmPassword');
  await waitForExpect(() => {
    const { value } = document.querySelector('input[name="confirmPassword"]');
    log.debug(`confirm password value="${value}"`);
    expect(value).toBe(password);
    log.debug('expect completed');
  });
  log.debug('done');
}

function waitForCondition(fn, { timeout = 2000 } = {}) {
  const endTime = Date.now() + timeout;
  return new Promise((resolve, reject) => {
    if (fn() === true) {
      resolve();
      return;
    }
    const timer = setInterval(() => {
      if (fn() === true) {
        clearInterval(timer);
        resolve();
        return;
      }
      if (Date.now() >= endTime) {
        clearInterval(timer);
        reject('timeout');
      }
    }, 50);
  });
}

describe('RegisterForm component', () => {

  afterEach(log.resetLevel);

  it('registers a new user', async () => {
    const props = {
      onSubmit: jest.fn(() => Promise.resolve(true)),
      onCancel: jest.fn(),
      checkUser: jest.fn(() => Promise.resolve(true))
    };
    const newUser = {
      username: 'anewuser',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    };
    const result = renderWithProviders(
      <RegisterForm {...props} />);
    result.getByText("Register");
    //log.setLevel('debug');
    await setAddUserFields(result, newUser);
    fireEvent.click(screen.getByText('Register'));
    await waitForCondition(() => {
      log.debug(`length=${props.onSubmit.mock.calls.length}`);
      return props.onSubmit.mock.calls.length === 1;
    });
    expect(props.onSubmit).toHaveBeenCalledTimes(1);
    expect(props.onSubmit.mock.calls).toEqual([[{
      ...newUser,
      confirmPassword: newUser.password
    }]]);
    return true;
  });

  it('refuses to register a user with a username that is too short', async () => {
    const newUser = {
      username: 'ab',
      email: 'new.user@music.bingo',
      password: 'my.weak.secret'
    };
    const props = {
      onSubmit: jest.fn(() => Promise.resolve(true)),
      onCancel: jest.fn(),
      checkUser: jest.fn(() => Promise.resolve(true))
    };

    const result = renderWithProviders(
      <RegisterForm {...props} />);
    result.getByText("Register");
    await setAddUserFields(result, newUser);
    await screen.findByDisplayValue(newUser.email);
    expect(screen.getByText('Register')).toBeDisabled();
    return true;
  });
});