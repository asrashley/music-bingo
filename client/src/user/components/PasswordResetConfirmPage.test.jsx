import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';
import { reverse } from 'named-urls';

import routes from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { PasswordResetConfirmPage, PasswordResetConfirmPageComponent } from './PasswordResetConfirmPage';

describe('PasswordResetConfirmPage component', () => {
  let apiMocks;

  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  afterAll(() => jest.useRealTimers());

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  it('renders without throwing an exception with initial state', () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      token: 'token'
    };
    const result = renderWithProviders(<PasswordResetConfirmPageComponent {...props} />);
    result.getByText(/Confirm New Password/);
    expect(result.asFragment()).toMatchSnapshot();
  });

  it('redirects if cancel is clicked', async () => {
    const url = await new Promise((resolve) => {
      const store = createStore(initialState);
      const props = {
        dispatch: store.dispatch,
        history: {
          push: resolve
        },
        token: 'token'
      };
      renderWithProviders(<PasswordResetConfirmPageComponent {...props} />);
      fireEvent.click(screen.getByText("Cancel"));
    });
    expect(url).toEqual(reverse(`${routes.login}`));
  });

  it('sets a new password', async () => {
    const store = createStore(initialState);
    const token = 'a.token';
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      match: {
        params: {
          token
        }
      }
    };
    const email = 'my.email@address.example';
    const password = 'new.password';
    //log.setLevel('debug');
    const payload = await new Promise((resolve) => {
      fetchMock.post('/api/user/reset', (url, opts) => {
        const body = JSON.parse(opts.body);
        resolve(body);
        const { email } = body;
        return apiMocks.jsonResponse({
          email,
          success: true
        });
      });
      renderWithProviders(<PasswordResetConfirmPage {...props} />);
      setFormFields([{
        label: /^Email address/,
        value: email
      }, {
        label: /^New Password/,
        value: password
      }, {
        label: /^Confirm New Password/,
        value: password
      }]);
      fireEvent.click(screen.getByText("Reset Password"));
    });
    expect(payload).toEqual({
      confirmPassword: password,
      email,
      password,
      token
    });
  });

  it('shows an error message if change password fails', async () => {
    const store = createStore(initialState);
    const token = 'a.token';
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      match: {
        params: {
          token
        }
      }
    };
    const email = 'my.email@address.example';
    const password = 'new.password';
    const error = 'an error message';
    //log.setLevel('debug');
    const payload = await new Promise((resolve) => {
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
      renderWithProviders(<PasswordResetConfirmPage {...props} />);
      setFormFields([{
        label: /^Email address/,
        value: email
      }, {
        label: /^New Password/,
        value: password
      }, {
        label: /^Confirm New Password/,
        value: password
      }]);
      fireEvent.click(screen.getByText("Reset Password"));
    });
    expect(payload).toEqual({
      confirmPassword: password,
      email,
      password,
      token
    });
    await screen.findByText(error);
  });
});
