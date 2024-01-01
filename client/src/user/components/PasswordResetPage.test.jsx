import React from 'react';
import { vi } from 'vitest';
import log from 'loglevel';
import { reverse } from 'named-urls';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { PasswordResetPage } from './PasswordResetPage';
import user from '../../fixtures/userState.json';

describe('PasswordResetPage component', () => {
  let apiMocks;

  beforeAll(() => {
    //vi.useFakeTimers('modern');
    //vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    vi.resetAllMocks();
  });

  //afterAll(() => vi.useRealTimers());

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  it('renders without throwing an exception with initial state', async () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      user
    };
    const { findByText, asFragment } = renderWithProviders(
      <PasswordResetPage {...props} />, { store });
    await findByText("Request Password Reset");
    expect(asFragment()).toMatchSnapshot();
  });

  it('requests a password reset email', async () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      user
    };
    const email = 'my.email@address.example';
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
    const { events, findByText, getByText } = renderWithProviders(
      <PasswordResetPage {...props} />, { store });
    await setFormFields([{
      label: /^Email address/,
      value: email
    }], events);
    await events.click(getByText("Request Password Reset"));
    await expect(payloadProm).resolves.toEqual({
      email
    });
    await findByText(`A password reset has been sent to ${email}`);
  });

  it('redirects if cancel is clicked', async () => {
    const pushProm = new Promise((resolve) => {
      vi.spyOn(reduxReactRouter, 'push').mockImplementationOnce((url) => {
        resolve(url);
        return {
          type: 'change-location',
          payload: {
            url,
          },
        };
      });
    });
    const props = {
      user: initialState.user,
      dispatch: vi.fn(),
    };
    const { events, findByText } = renderWithProviders(<PasswordResetPage {...props} />);
    await events.click(await findByText("Cancel"));
    await expect(pushProm).resolves.toEqual(reverse(`${routes.login}`));
  });
});
