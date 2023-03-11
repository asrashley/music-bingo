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
import * as user from '../../fixtures/userState.json';
import { current } from '@reduxjs/toolkit';

describe('ChangeUserPage component', () => {
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

  it('changes password when submit is clicked', async () => {
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
    await new Promise((resolve) => {
      fetchMock.post('/api/user/modify', (url, opts) => {
        const { existingPassword, email, password, confirmPassword } = JSON.parse(opts.body);
        expect(existingPassword).toEqual(currentPassword);
        expect(password).toEqual(newPassword);
        expect(confirmPassword).toEqual(newPassword);
        const response = {
          email,
          success: true
        };
        resolve(response);
        return apiMocks.jsonResponse(response);
      });
      //log.setLevel('debug');
      renderWithProviders(<ChangeUserPage {...props} />);
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
    });
  });

});
