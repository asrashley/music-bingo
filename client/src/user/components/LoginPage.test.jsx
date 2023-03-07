import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { LoginPage } from './LoginPage';

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

describe('LoginPage component', () => {
  let store;
  let apiMock;

  beforeEach(() => {
    store = createStore(initialState);
    apiMock = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('renders from initial state', () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const result = renderWithProviders(<LoginPage {...props} />, { store });
    result.getByLabelText("User name or email address", { exact: false });
  });

  it('login page matches snapshot', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
   };
    const { asFragment } = renderWithProviders(<LoginPage {...props} />);
    await screen.findByText('Login');
    expect(asFragment()).toMatchSnapshot();
  });

  it('redirects page when login is successful', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<LoginPage {...props} />);
    setUsernameAndPassword(expected);
    fireEvent.submit(await screen.findByText('Login'));
    await screen.findByText('Logging in..');
    waitForExpect(() => {
      expect(history.push).toHaveBeenCalledTimes(1);
    });
  });

  it('shows error message when username or password is wrong', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      username: 'user',
      password: 'wrongpassword',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<LoginPage {...props} />);
    setUsernameAndPassword(expected);
    fireEvent.submit(await screen.findByText('Login'));
    await screen.findByText("Username or password is incorrect");
  });

  it('shows error message when there is a server fault', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<LoginPage {...props} />);
    setUsernameAndPassword(expected);
    apiMock.setServerStatus(500);
    fireEvent.submit(await screen.findByText('Login'));
    await screen.findByText("There is a problem with the server. Please try again later");
  });

});
