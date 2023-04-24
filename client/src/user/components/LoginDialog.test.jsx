import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import * as user from '../../fixtures/userState.json';

import { LoginDialog } from './LoginDialog';

function setUsernameAndPassword({ username, password }) {
  const userField = screen.getByLabelText("User name or email address", { exact: false });
  fireEvent.input(userField, {
    target: {
      value: username
    }
  });
  const pwdField = screen.getByLabelText('Password', { exact: false });
  fireEvent.input(pwdField, {
    target: {
      value: password
    }
  });
}

describe('LoginDialog component', () => {
  let store;
  let apiMock;

  beforeEach(() => {
    store = createStore({
      ...initialState,
      user
    });
    apiMock = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('renders from initial state', () => {
    const { dispatch } = store;
    const props = {
      user: initialState.user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
      backdrop: true
    };
    const result = renderWithProviders(<LoginDialog {...props} />, { store });
    result.getByLabelText("User name or email address", { exact: false });
  });

  it('login dialog matches snapshot', () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
      backdrop: true
    };
    const { asFragment } = renderWithProviders(<LoginDialog {...props} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it('calls onCancel when cancel button is pressed', () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
    };
    const result = renderWithProviders(<LoginDialog {...props} />);
    fireEvent.click(result.getByRole('button', { name: "Close" }));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onSuccess when submit is successful', async () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    renderWithProviders(<LoginDialog {...props} />);
    setUsernameAndPassword(expected);
    fireEvent.submit(screen.getByText('Login'));
    await screen.findByText('Logging in..');
    await waitForExpect(() => {
      expect(props.onSuccess).toHaveBeenCalledTimes(1);
    });
  });

  it('shows error message when username or password is wrong', async () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
    };
    const expected = {
      username: 'user',
      password: 'wrongpassword',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<LoginDialog {...props} />);
    setUsernameAndPassword(expected);
    fireEvent.submit(screen.getByText('Login'));
    await screen.findByText("Username or password is incorrect");
  });

  it('shows error message when there is a server fault', async () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: jest.fn(),
      onSuccess: jest.fn(),
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<LoginDialog {...props} />);
    setUsernameAndPassword(expected);
    apiMock.setServerStatus(500);
    fireEvent.submit(screen.getByText('Login'));
    await screen.findByText("There is a problem with the server. Please try again later");
  });

});
