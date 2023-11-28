import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import fetchMock from "fetch-mock-jest";
import log from 'loglevel';
import { reverse } from 'named-urls';

import routes from '../../routes';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { renderWithProviders, installFetchMocks, setFormFields } from '../../testHelpers';
import { ChangeUserPage } from './ChangeUserPage';
import { MessagePanel } from '../../messages/components/MessagePanel';

import * as user from '../../fixtures/userState.json';

describe('ChangeUserPage component', () => {
  let apiMocks;

  beforeEach(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    apiMocks = installFetchMocks(fetchMock, { loggedIn: false });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    jest.useRealTimers();
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
    const result = renderWithProviders(<ChangeUserPage {...props} />);
    result.getByText('Confirm New Password');
    result.getByText('Change password');
  });

  it('redirects page if cancel is clicked', async () => {
    const store = createStore(initialState);
    const url = await new Promise((resolve) => {
      const props = {
        dispatch: store.dispatch,
        history: {
          push: resolve
        },
        user
      };
      const result = renderWithProviders(<ChangeUserPage {...props} />);
      fireEvent.click(result.getByText('Cancel'));
    });
    expect(url).toEqual(reverse(`${routes.user}`));
  });

  it.each([
    ['changes password when submit is clicked', true],
    ['handles server error when submit is clicked', false]
  ])('%s', async (_, successful) => {
    const store = createStore(initialState);
    const props = {
      dispatch: store.dispatch,
      history: {
        push: jest.fn()
      },
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
    renderWithProviders(<div>
      <MessagePanel />
      <ChangeUserPage {...props} /></div>);
    setFormFields([{
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
    }]);
    fireEvent.click(screen.getByText("Change password"));
    const result = await modifyApiPromise;
    if (successful) {
      expect(result).toEqual({ email, success: true });
      console.dir(store.getState().messages.messages);
      await screen.findByText('Password successfully updated');
      expect(props.history.push).toHaveBeenCalledTimes(1);
    } else {
      expect(result).toEqual(500);
      expect(props.history.push).toHaveBeenCalledTimes(0);
      await screen.findAllByText('500: Internal Server Error');
    }
  });

});
