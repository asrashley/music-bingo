import React from 'react';
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';

import { LoginDialogForm } from './LoginDialogForm';

describe('LoginDialogForm component', () => {
  it('login form matches snapshot', async () => {
    const userData = await import('../../fixtures/userState.json');
    const props = {
      alert: "an alert",
      user: userData['default'],
      onSubmit: () => true,
      onCancel: () => true,
    };
    props.user.username = '';
    props.user.email = '';
    const { asFragment } = renderWithProviders(<LoginDialogForm {...props} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it('calls onCancel when cancel button is pressed', async () => {
    const userData = await import('../../fixtures/userState.json');
    const props = {
      user: userData['default'],
      onSubmit: jest.fn(),
      onCancel: jest.fn(),
    };
    const result = renderWithProviders(<LoginDialogForm {...props} />);
    fireEvent.click(result.getByRole('button', { name: "Close" }));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onSubmit when submit button is pressed', async () => {
    const userData = await import('../../fixtures/userState.json');
    let loginProps = null;
    const mockLogin = jest.fn((props) => {
      loginProps = props;
      return Promise.resolve(true);
    });
    const props = {
      user: userData['default'],
      onSubmit: mockLogin,
      onCancel: jest.fn(),
    };
    const expected = {
      username: 'a.user@unit.test',
      password: 'a.secret',
      rememberme: false
    };
    renderWithProviders(<LoginDialogForm {...props} />);
    const userField = screen.getByLabelText("User name or email address", { exact: false });
    fireEvent.input(userField, {
      target: {
        value: expected.username
      }
    });
    //setTextField(userField, 'a.user@unit.test');
    expect(screen.getByLabelText("User name or email address", { exact: false }).value).toBe('a.user@unit.test');
    const pwdField = screen.getByLabelText('Password', { exact: false });
    fireEvent.input(pwdField, {
      target: {
        value: expected.password
      }
    });
    fireEvent.submit(screen.getByText('Login'));
    //expect(mockLogin).toHaveBeenCalledTimes(1);
    await screen.findByText('Logging in..');
    expect(loginProps).not.toBeNull();
    expect(loginProps).toStrictEqual(expected);
  });

  it('shows an error if username is not provided', async () => {
    const userData = await import('../../fixtures/userState.json');
    let loginProps = null;
    const mockLogin = jest.fn((props) => {
      loginProps = props;
      return Promise.resolve(true);
    });
    const props = {
      user: userData['default'],
      onSubmit: mockLogin,
      onCancel: jest.fn(),
    };
    const expected = {
      username: '',
      password: 'a.secret',
      rememberme: false
    };
    renderWithProviders(<LoginDialogForm {...props} />);
    let userField = screen.getByLabelText("User name or email address", { exact: false });
    fireEvent.input(userField, {
      target: {
        value: expected.username
      }
    });
    let pwdField = screen.getByLabelText('Password', { exact: false });
    fireEvent.input(pwdField, {
      target: {
        value: expected.password
      }
    });
    fireEvent.submit(screen.getByText('Login'));
    userField = await screen.findByLabelText("User name or email address", { exact: false });
    expect(loginProps).toBeNull();
    expect(userField).toHaveClass('is-invalid');
    pwdField = screen.getByLabelText('Password', { exact: false });
    expect(pwdField).not.toHaveClass('is-invalid');
  });

});



