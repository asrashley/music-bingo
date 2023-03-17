import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { RegisterPage } from './RegisterPage';

import * as user from '../../fixtures/userState.json';

function setFormValues({ email, username, password }) {
  setFormFields([
    {
      label: "Email address",
      value: email,
      exact: false
    },
    {
      label: "Username",
      value: username,
      exact: false
    },
    {
      label: /^Password/,
      value: password
    },
    {
      label: /^Confirm Password/,
      value: password
    },
  ]);
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
      email: 'successful@unit.test',
      username: 'newuser',
      password: '!secret!',
      rememberme: false
    };
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
    if (field === 'username') {
      apiMock.addUser({
        email: 'a.different@email.net',
        username: expected.username
      });
    } else {
      apiMock.addUser({
        email: expected.email,
        username: 'anotheruser'
      });
    }
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
    fetchMock.put('/api/user', (url, opts) => {
      return 500;
    });
    fireEvent.submit(await screen.findByText('Register'));
    await screen.findAllByText("500: Internal Server Error");
  });

  it('shows error message from server', async () => {
    const { dispatch } = store;
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch,
      history
    };
    const expected = {
      email: 'successful@unit.test',
      username: 'newuser',
      password: '!secret!',
      rememberme: false
    };
    const addUserApi = jest.fn((url, opts) => {
      const { email, username, password } = JSON.parse(opts.body);
      expect(email).toBe(expected.email);
      expect(username).toBe(expected.username);
      expect(password).toBe(expected.password);
      return apiMock.jsonResponse({
        'success': false,
        'error': {
          'username': `Username ${username} is already taken`
        },
        user: {
          email,
          username
        }
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
    await screen.findByText(`Username ${expected.username} is already taken`);
  });

});
