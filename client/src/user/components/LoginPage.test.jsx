import React from 'react';
import { screen } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import { push } from '@lagunovsky/redux-react-router';
import { reverse } from 'named-urls';
import log from 'loglevel';

import {
  fetchMock,
  renderWithProviders,
  installFetchMocks,
  setFormFields
} from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { routes } from '../../routes/routes';

import { LoginPage } from './LoginPage';

async function setUsernameAndPassword({ username, password }, events) {
  await setFormFields([{
    label: "User name or email address",
    value: username,
    exact: false,
  }, {
    label: /^Password/,
    value: password,
  }], events);
}

describe('LoginPage component', () => {
  let apiMock;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('renders from initial state', async () => {
    const { findByLabelText } = renderWithProviders(<LoginPage />);
    await findByLabelText("User name or email address", { exact: false });
  });

  it('login page matches snapshot', async () => {
    const { asFragment, findByText } = renderWithProviders(<LoginPage />);
    await findByText('Login');
    expect(asFragment()).toMatchSnapshot();
  });

  it('redirects page when login is successful', async () => {
    const store = createStore(initialState);
    const history = createMemoryHistory({
      initialEntries: ['/', '/user/login'],
      initialIndex: 1,
    });
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    const dispatchSpy = vi.spyOn(store, 'dispatch');
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(<LoginPage />, { store, history });
    await setUsernameAndPassword(expected, events);
    await events.click(await findByText('Login'));
    await findByText('Welcome user', { exact: false });
    expect(dispatchSpy).toHaveBeenCalledWith(push(reverse(`${routes.index}`)));
  });

  it('shows error message when username or password is wrong', async () => {
    const expected = {
      username: 'user',
      password: 'wrongpassword',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(<LoginPage />);
    await setUsernameAndPassword(expected, events);
    await events.click(await screen.findByText('Login'));
    await findByText("Username or password is incorrect");
  });

  it('shows error message when there is a server fault', async () => {
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(<LoginPage />);
    await setUsernameAndPassword(expected, events);
    apiMock.setServerStatus(500);
    await events.click(await screen.findByText('Login'));
    await findByText("There is a problem with the server. Please try again later");
  });

});
