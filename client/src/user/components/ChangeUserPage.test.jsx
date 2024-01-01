import React from 'react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { ChangeUserPage, ChangeUserPageComponent } from './ChangeUserPage';
import { MessagePanel } from '../../messages/components/MessagePanel';

import user from '../../fixtures/userState.json';

describe('ChangeUserPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation(url => ({
    type: 'change-location',
    payload: {
      url,
    },
  }));
  let apiMocks;

  beforeEach(() => {
    //vi.useFakeTimers('modern');
    //vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    pushSpy.mockClear();
    log.resetLevel();
    //vi.useRealTimers();
  });

  it('renders without throwing an exception with initial state', () => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      user
    };
    const { getByText } = renderWithProviders(<ChangeUserPageComponent {...props} />, { store });
    getByText('Confirm New Password');
    getByText('Change password');
  });

  it('redirects page if cancel is clicked', async () => {
    const store = createStore(initialState);
    const pushProm = new Promise((resolve) => {
      pushSpy.mockImplementationOnce((url) => {
        resolve(url);
        return {
          type: 'change-location',
          payload: {
            url,
          },
        };
      });
    });
    const { events, getByText } = renderWithProviders(<ChangeUserPage dispatch={store.dispatch} user={user} />, { store });
    await events.click(getByText('Cancel'));
    await Promise.resolve();
    await expect(pushProm).resolves.toEqual(reverse(`${routes.user}`));
  });

  it.each([
    ['changes password when submit is clicked', true],
    ['handles server error when submit is clicked', false]
  ])('%s', async (_, successful) => {
    log.setLevel('silent');
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      user
    };
    const email = 'my.email@address.example';
    const currentPassword = 'mysecret';
    const newPassword = 'my.new.password';
    const modifyApiPromise = new Promise((resolve) => {
      fetchMock.post('/api/user/modify', (url, opts) => {
        const { existingPassword, email, password, confirmPassword } = JSON.parse(opts.body);
        expect(existingPassword).toEqual(currentPassword);
        expect(password).toEqual(newPassword);
        expect(confirmPassword).toEqual(newPassword);
        if (!successful) {
          resolve(500);
          return 500;
        }
        const response = {
          email,
          success: true
        };
        resolve(response);
        return apiMocks.jsonResponse(response);
      });
    });
    const { events, findByText, getByText, findAllByText } = renderWithProviders(<div>
      <MessagePanel />
      <ChangeUserPage {...props} /></div>, { store });
    await setFormFields([{
      label: /^Email address/,
      value: email
    }, {
      label: 'Existing Password',
      value: currentPassword,
      exact: false
    }, {
      label: /^New Password/,
      value: newPassword,
    }, {
      label: /^Confirm New Password/,
      value: newPassword
    }], events);
    await events.click(getByText("Change password"));
    const result = await modifyApiPromise;
    if (successful) {
      expect(result).toEqual({ email, success: true });
      //console.dir(store.getState().messages.messages);
      await findByText('Password successfully updated');
      expect(pushSpy).toHaveBeenCalledTimes(1);
      expect(pushSpy).toHaveBeenCalledWith(reverse(`${routes.user}`));
    } else {
      expect(result).toEqual(500);
      expect(pushSpy).not.toHaveBeenCalled();
      await findAllByText('500: Internal Server Error');
    }
  });

});
