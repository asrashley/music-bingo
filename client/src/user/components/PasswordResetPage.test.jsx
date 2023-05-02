import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';
import { reverse } from 'named-urls';

import routes from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { PasswordResetPage, PasswordResetPageComponent } from './PasswordResetPage';
import * as user from '../../fixtures/userState.json';

describe('PasswordResetPage component', () => {
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
      user
    };
    const result = renderWithProviders(<PasswordResetPage {...props} />);
    result.getByText("Request Password Reset");
    expect(result.asFragment()).toMatchSnapshot();
  });

  it('requests a password reset email', async () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
      user
    };
    const email = 'my.email@address.example';
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
      renderWithProviders(<PasswordResetPage {...props} />);
      setFormFields([{
        label: /^Email address/,
        value: email
      }]);
      fireEvent.click(screen.getByText("Request Password Reset"));
    });
    expect(payload).toEqual({
      email
    });
  });

  it('redirects if cancel is clicked', async () => {
    const url = await new Promise((resolve) => {
      const props = {
        user: initialState.user,
        dispatch: jest.fn(),
        history: {
          push: resolve
        }
      };
      renderWithProviders(<PasswordResetPage {...props} />);
      fireEvent.click(screen.getByText("Cancel"));
    });
    expect(url).toEqual(reverse(`${routes.login}`));
  });
});
