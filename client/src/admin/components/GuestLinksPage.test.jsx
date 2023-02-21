import React from 'react';
import { fireEvent, screen, getByRole } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import { reverse } from 'named-urls';
import waitForExpect from 'wait-for-expect'

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import routes from '../../routes';
import { GuestLinksPage } from './GuestLinksPage';

describe('GuestLinksPage component', () => {
  let apiMock = null;

  beforeEach(() => {
    apiMock = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMock = null;
  });

  it('to shows a list of guest links', async () => {
    const [userData, guestData] = await Promise.all([
      import('../../fixtures/userState.json'),
      import('../../fixtures/user/guest.json')
    ]);
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const history = {
      push: jest.fn()
    };
    const { asFragment } = renderWithProviders(<GuestLinksPage history={history} />, { store });
    await Promise.all(guestData['default'].map((token) => {
      const link = reverse(`${routes.guestAccess}`, { token: token.jti });
      return screen.findByText(link);
    }));
    expect(asFragment()).toMatchSnapshot();
  });

  it('to allows a guest link to be added', async () => {
    const userData = await import('../../fixtures/userState.json');
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const history = {
      push: jest.fn()
    };
    const token = {
      "pk": 46,
      "jti": "cT34TCj7vg",
      "token_type": 3,
      "username": "cT34TCj7vg",
      "created": "2023-02-20T08:12:54Z",
      "expires": "2023-02-27T08:12:54.014843Z",
      "revoked": false,
      "user": null
    };
    const addLinkApi = jest.fn(() => apiMock.jsonResponse({
      success: true,
      token
    }));
    fetchMock.put('/api/user/guest/add', addLinkApi);
    //log.setLevel('debug');
    const result = renderWithProviders(<GuestLinksPage history={history} />, { store });
    fireEvent.click(screen.getByText('Add link'));
    await waitForExpect(() => {
      expect(addLinkApi).toHaveBeenCalledTimes(1);
    });
    await screen.findByText(token.jti, { exact: false });
  });

  it('to allows a guest link to be deleted', async () => {
    const userData = await import('../../fixtures/userState.json');
    const guestData = await import('../../fixtures/user/guest.json');
    const store = createStore({
      ...initialState,
      admin: {
        ...initialState.admin,
        user: userData['default'].pk
      },
      user: userData['default']
    });
    const history = {
      push: jest.fn()
    };
    renderWithProviders(<GuestLinksPage history={history} />, { store });
    const link = reverse(`${routes.guestAccess}`, { token: guestData[0].jti });
    await screen.findByText(link);
    const deleteLinkApi = jest.fn(() => apiMock.jsonResponse('', 204));
    fetchMock.delete(`/api/user/guest/delete/${guestData[0].jti}`, deleteLinkApi);
    const row = screen.getByTestId(`token.${guestData[0].pk}`);
    fireEvent.click(getByRole(row, 'button'));
    await waitForExpect(() => {
      expect(deleteLinkApi).toHaveBeenCalledTimes(1);
    })
  });

});
