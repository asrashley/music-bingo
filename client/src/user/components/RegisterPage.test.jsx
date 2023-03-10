import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { RegisterPage } from './RegisterPage';

import * as user from '../../fixtures/userState.json';

function setFormValues({ email, username, password }) {
  const emailField = screen.getByLabelText("Email address", { exact: false });
  fireEvent.input(emailField, {
    target: {
      value: email
    }
  });

  const userField = screen.getByLabelText("Username", { exact: false });
  fireEvent.input(userField, {
    target: {
      value: username
    }
  });
  const pwdField = screen.getByLabelText(/^Password/);
  fireEvent.input(pwdField, {
    target: {
      value: password
    }
  });
  const confirmField = screen.getByLabelText('Confirm Password', { exact: false });
  fireEvent.input(confirmField, {
    target: {
      value: password
    }
  });
}

describe('RegisterPage component', () => {
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
    const result = renderWithProviders(<RegisterPage {...props} />, { store });
    expect(result.asFragment()).toMatchSnapshot();
  });

  it('redirects page when register is successful', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      email: 'a.user@example.tld',
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    fetchMock.post('/api/user/check', (url, opts) => {
      const response = {
        "username": false,
        "email": false
      };
      return apiMock.jsonResponse(response);
    });
    const addUserApi = jest.fn((url, opts) => {
      const { email, username, password } = JSON.parse(opts.body);
      expect(email).toBe(expected.email);
      expect(username).toBe(expected.username);
      expect(password).toBe(expected.password);
      return apiMock.jsonResponse({
        'message': 'Successfully registered',
        'success': true,
        'user': {
          ...user,
          email,
          username,
          groups: ["users"]
        },
        'accessToken': apiMock.getAccessToken(),
        'refreshToken': apiMock.getRefreshToken(),
      });
    });
    fetchMock.put('/api/user', addUserApi);
    //log.setLevel('debug');
    renderWithProviders(<RegisterPage {...props} />);
    //screen.debug();
    setFormValues(expected);
    fireEvent.submit(await screen.findByText('Register'));
    await waitForExpect(() => {
      expect(addUserApi).toHaveBeenCalledTimes(1);
    });
    await waitForExpect(() => {
      expect(history.push).toHaveBeenCalledTimes(1);
    });
  });

  it.each(['username', 'email'])('shows error message when %s is already in use', async (field) => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      email: 'a.user@example.tld',
      username: 'user',
      password: 'wrongpassword',
      rememberme: false
    };
    fetchMock.post('/api/user/check', (url, opts) => {
      const response = {
        "username": false,
        "email": false,
        [field]: true
      };
      return apiMock.jsonResponse(response);
    });
    //log.setLevel('debug');
    renderWithProviders(<RegisterPage {...props} />);
    setFormValues(expected);
    fireEvent.submit(await screen.findByText('Register'));
    if (field === 'email') {
      await screen.findByText('That email address is already registered');
    } else {
      await screen.findByText('That username is already taken');
    }
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
      email: 'a.user@example.tld',
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    renderWithProviders(<RegisterPage {...props} />);
    setFormValues(expected);
    apiMock.setServerStatus(500);
    fetchMock.post('/api/user/check', (url, opts) => {
      return 500;
    });
    fireEvent.submit(await screen.findByText('Register'));
    await screen.findAllByText("There is a problem with the server. Please try again later");
  });

});
