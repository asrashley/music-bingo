import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';
import fetchMock from 'fetch-mock';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import {
  renderWithProviders,
  installFetchMocks,
  setFormFields
} from '../../../tests';
import { PasswordResetConfirmPage, PasswordResetConfirmPageComponent } from './PasswordResetConfirmPage';

describe('PasswordResetConfirmPage component', () => {
  let mockServer;

  beforeEach(() => {
    mockServer = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    mockServer.shutdown();
    log.resetLevel();
    fetchMock.reset();
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
    const payloadProm = mockServer.addResponsePromise('/api/user/reset', 'POST');
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
    const { body, status } = await payloadProm;
    expect(status).toEqual(200);
    expect(JSON.parse(body)).toEqual({
      email,
      success: true,
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
    const payloadProm = mockServer.addResponsePromise('/api/user/reset', 'POST');
    mockServer.setResponseModifier('/api/user/reset', 'POST', () => {
      return {
        email,
        error,
        success: false
      };
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
    const { body, status } = await payloadProm;
    expect(status).toEqual(200);
    expect(JSON.parse(body)).toEqual({
      email,
      error,
      success: false,
    });
    await screen.findByText(error);
  });
});
