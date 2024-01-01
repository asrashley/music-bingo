import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { PasswordResetConfirmPage, PasswordResetConfirmPageComponent } from './PasswordResetConfirmPage';

describe('PasswordResetConfirmPage component', () => {
  let apiMocks;

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('renders without throwing an exception with initial state', async () => {
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          token: 'token',
        }
      }
    });
    const { findByText, asFragment } = renderWithProviders(
      <PasswordResetConfirmPageComponent dispatch={store.dispatch} token="token" />, { store });
    await findByText(/Confirm New Password/);
    expect(asFragment()).toMatchSnapshot();
  });

  it('redirects if cancel is clicked', async () => {
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          token: 'token',
        }
      }
    });
    const url = await new Promise((resolve) => {
      vi.spyOn(reduxReactRouter, 'push').mockImplementationOnce((url) => {
        resolve(url);
        return {
          type: 'change-location',
          payload: { url },
        };
      });
      renderWithProviders(
        <PasswordResetConfirmPageComponent dispatch={store.dispatch} token="token" />, { store });
      fireEvent.click(screen.getByText("Cancel"));
    });
    expect(url).toEqual(reverse(`${routes.login}`));
  });

  it('sets a new password', async () => {
    const token = 'a.token';
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          token
        }
      }
    });
    const email = 'my.email@address.example';
    const password = 'new.password';
    //log.setLevel('debug');
    const payloadProm = new Promise((resolve) => {
      fetchMock.post('/api/user/reset', (url, opts) => {
        const body = JSON.parse(opts.body);
        resolve(body);
        const { email } = body;
        return apiMocks.jsonResponse({
          email,
          success: true
        });
      });
    });
    const { events, getByText } = renderWithProviders(<PasswordResetConfirmPage dispatch={store.dispatch} />, { store });
    await setFormFields([{
      label: /^Email address/,
      value: email
    }, {
      label: /^New Password/,
      value: password
    }, {
      label: /^Confirm New Password/,
      value: password
    }], events);
    await events.click(getByText("Reset Password"));
    await expect(payloadProm).resolves.toEqual({
      confirmPassword: password,
      email,
      password,
      token
    });
  });

  it('shows an error message if change password fails', async () => {
    const token = 'a.token';
    const store = createStore({
      ...initialState,
      routes: {
        params: {
          token
        }
      }
    });
    const email = 'my.email@address.example';
    const password = 'new.password';
    const error = 'an error message';
    //log.setLevel('debug');
    const payloadProm = new Promise((resolve) => {
      fetchMock.post('/api/user/reset', (url, opts) => {
        const body = JSON.parse(opts.body);
        resolve(body);
        const { email } = body;
        return apiMocks.jsonResponse({
          email,
          error,
          success: false
        });
      });
    });
    const { events } = renderWithProviders(<PasswordResetConfirmPage dispatch={store.dispatch} />, { store });
    await setFormFields([{
      label: /^Email address/,
      value: email
    }, {
      label: /^New Password/,
      value: password
    }, {
      label: /^Confirm New Password/,
      value: password
    }], events);
    await events.click(screen.getByText("Reset Password"));
    await expect(payloadProm).resolves.toEqual({
      confirmPassword: password,
      email,
      password,
      token
    });
    await screen.findByText(error);
  });
});
