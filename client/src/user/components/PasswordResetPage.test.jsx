import React from 'react';
import { vi } from 'vitest';
import log from 'loglevel';
import { reverse } from 'named-urls';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks, setFormFields } from '../../../tests';
import { PasswordResetPage } from './PasswordResetPage';
import user from '../../../tests/fixtures/userState.json';

describe('PasswordResetPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    vi.resetAllMocks();
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
    const { events, findByText, getByText } = renderWithProviders(
      <PasswordResetPage {...props} />, { store });
    await setFormFields([{
      label: /^Email address/,
      value: email
    }], events);
    await events.click(getByText("Request Password Reset"));
    await findByText(`A password reset has been sent to ${email}`);
    expect(fetchMock.calls('/api/user/reset', 'POST').length).toEqual(1);
    expect(JSON.parse(fetchMock.lastOptions('/api/user/reset', 'POST').body)).toEqual({
      email
    });
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
