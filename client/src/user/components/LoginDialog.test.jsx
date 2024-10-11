import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';
import fetchMock from 'fetch-mock';

import { renderWithProviders, installFetchMocks, setFormFields } from '../../../tests';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import user from '../../../tests/fixtures/userState.json';

import { LoginDialog } from './LoginDialog';

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
    fetchMock.reset();
    log.resetLevel();
    apiMock = null;
  });

  it('renders from initial state', () => {
    const { dispatch } = store;
    const props = {
      user: initialState.user,
      dispatch,
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
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
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
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
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
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
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    const { events } = renderWithProviders(<LoginDialog {...props} />);
    await setFormFields([{
      label: "User name or email address",
      value: expected.username,
      exact: false
    }, {
      label: /^Password/,
      value: expected.password,
      exact: false
    }], events);
    //log.setLevel('debug');
    await events.click(screen.getByText('Login'));
    await waitForExpect(() => {
      expect(props.onSuccess).toHaveBeenCalledTimes(1);
    });
  });

  it('shows error message when username or password is wrong', async () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
    };
    const expected = {
      username: 'user',
      password: 'wrongpassword',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText } = renderWithProviders(<LoginDialog {...props} />);
    await setFormFields([{
      label: "User name or email address",
      value: expected.username,
      exact: false
    }, {
      label: 'Password',
      value: expected.password,
      exact: false
    }], events);
    await events.click(screen.getByText('Login'));
    await findByText("Username or password is incorrect");
  });

  it('shows error message when there is a server fault', async () => {
    const { dispatch } = store;
    const props = {
      user,
      dispatch,
      onCancel: vi.fn(),
      onSuccess: vi.fn(),
    };
    const expected = {
      username: 'user',
      password: 'mysecret',
      rememberme: false
    };
    //log.setLevel('debug');
    const { events, findByText, getByText } = renderWithProviders(<LoginDialog {...props} />);
    await setFormFields([{
      label: "User name or email address",
      value: expected.username,
      exact: false
    }, {
      label: 'Password',
      value: expected.password,
      exact: false
    }], events);
    apiMock.setServerStatus(500);
    await events.click(getByText('Login'));
    await findByText("There is a problem with the server. Please try again later");
  });

});
