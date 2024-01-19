import React from 'react';
import log from 'loglevel';
import { reverse } from 'named-urls';
import { waitFor } from '@testing-library/react';
import * as reduxReactRouter from '@lagunovsky/redux-react-router';

import { routes } from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { fetchMock, renderWithProviders, setFormFields } from '../../../tests';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { ChangeUserPage, ChangeUserPageComponent } from './ChangeUserPage';
import { MessagePanel } from '../../messages/components/MessagePanel';


describe('ChangeUserPage component', () => {
  const pushSpy = vi.spyOn(reduxReactRouter, 'push').mockImplementation(url => ({
    type: 'change-location',
    payload: {
      url,
    },
  }));
  let apiMock, user;

  beforeEach(() => {
    apiMock = new MockBingoServer(fetchMock, { currentUser: normalUser });
    user = apiMock.getUserState(normalUser);
  });

  afterEach(() => {
    apiMock.shutdown();
    apiMock = null;
    pushSpy.mockClear();
    log.resetLevel();
    vi.useRealTimers();
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
    const store = createStore({
      ...initialState, user
    });
    const props = {
      dispatch: store.dispatch,
      user
    };
    const email = 'my.email@address.example';
    const currentPassword = normalUser.password;
    const newPassword = 'my.new.password';
    const modifyApiPromise = apiMock.addResponsePromise('/api/user/modify', 'POST');
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
    if (!successful) {
      apiMock.setServerStatus(500);
      log.setLevel('silent');
    }
    await events.click(getByText("Change password"));
    let result;
    await waitFor(async () => {
      result = await modifyApiPromise;
    });
    if (successful) {
      expect(JSON.parse(result.body)).toEqual({
        email,
        success: true,
      });
      expect(result.status).toEqual(200);
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
