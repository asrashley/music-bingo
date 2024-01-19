import React from 'react';
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';
import { createMemoryHistory } from 'history';

import { fetchMock, renderWithProviders, setFormFields } from '../../../tests';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { MessagePanel } from '../../messages/components';
import { RegisterPage } from './RegisterPage';

import { routes } from '../../routes';

function RegisterPageTest(props) {
  return (<div className="container">
    <MessagePanel />
    <Routes>
      <Route path="/" element={<div>IndexPage</div>} />
      <Route path={routes.register} element={<RegisterPage {...props} />} />
    </Routes>
  </div>);
}

function setFormValues({ email, username, password }, events) {
  return setFormFields([
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
  ], events);
}

describe('RegisterPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation(url => ({
    type: 'push-location',
    payload: {
      url,
    },
  }));
  const history = createMemoryHistory({
    initialEntries: ['/', routes.register],
    initialIndex: 1,
  });

  let store;
  let apiMock;

  beforeEach(() => {
    store = createStore(initialState);
    apiMock = new MockBingoServer(fetchMock);
  });

  afterEach(() => {
    apiMock.shutdown();
    pushSpy.mockClear();
    log.resetLevel();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('renders from initial state', () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const result = renderWithProviders(<RegisterPageTest {...props} />, { store, history });
    expect(result.asFragment()).toMatchSnapshot();
  });

  it('redirects page when register is successful', async () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const expected = {
      email: 'successful@unit.test',
      username: 'newuser',
      password: '!secret!',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    //screen.debug();
    await setFormValues(expected, events);
    await events.click(await findByText('Register'));
    await waitForExpect(() => {
      expect(fetchMock.calls('/api/user', 'PUT').length).toEqual(1);
    });
    await waitForExpect(() => {
      expect(pushSpy).toHaveBeenCalledTimes(1);
    });
  });

  it('redirects page when cancel is called', async () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const { events, getByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    await events.click(getByText('Cancel'));
    expect(pushSpy).toHaveBeenCalledTimes(1);
  });

  it.each(['username', 'email'])('shows error message when %s is already in use', async (field) => {
    const { dispatch } = store;
    const props = {
      dispatch,
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
    const { events, findByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    await setFormValues(expected, events);
    await events.click(await screen.findByText('Register'));
    if (field === 'email') {
      await findByText('That email address is already registered');
    } else {
      await findByText('That username is already taken');
    }
  });

  it('shows error message when there is a server fault', async () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const expected = {
      email: 'a.user@example.tld',
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    const { events, findAllByText, findByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    await setFormValues(expected, events);
    apiMock.setServerStatus(500);
    await events.click(await findByText('Register'));
    await findAllByText("500: Internal Server Error");
  });

  it('shows error message if username is taken', async () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const expected = {
      email: 'successful@unit.test',
      username: normalUser.username,
      password: '!secret!',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    await setFormValues(expected, events);
    await events.click(await screen.findByText('Register'));
    await findByText('That username is already taken');
  });

  it('shows error message from server', async () => {
    const { dispatch } = store;
    const props = {
      dispatch,
    };
    const expected = {
      email: 'successful@unit.test',
      username: 'new.user',
      password: '!secret!',
      rememberme: false
    };
    apiMock.setResponseModifier('/api/user', 'PUT', (_url, _opts, data) => {
      if (data.username !== undefined && data.email !== undefined) {
        return data;
      }
      return {
        ...data,
        error: {
          username: `Username ${data.user.username} is already taken, choose another one`,
        },
        success: false,

      };
    });
    const { events, findByText } = renderWithProviders(
      <RegisterPageTest {...props} />, { store, history });
    await setFormValues(expected, events);
    await events.click(await screen.findByText('Register'));
    await findByText(`Username ${expected.username} is already taken, choose another one`);
  });

});
