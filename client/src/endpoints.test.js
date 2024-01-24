import log from 'loglevel';
import { describe, vi } from 'vitest';

import { api, fetchWithRetry, receiveStream } from './endpoints';
import { jsonResponse, fetchMock } from '../tests';
import { MockBingoServer, adminUser } from '../tests/MockServer';
import { createStore, initialState } from './store';
import { userSlice, refreshAccessToken } from './user/userSlice';

import settings from '../tests/fixtures/settings.json';

describe('endpoints - fetchWithRetry()', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    vi.useRealTimers();
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('uses refresh token to get a new access token', async () => {
    const refreshResult = {
      ok: true,
      status: 200,
      payload: {
        accessToken: 'a.new.token'
      }
    };
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: vi.fn(),
      success: vi.fn(),
      failure: vi.fn(),
      rejectErrors: false,
      headers: {
        cache: "no-cache",
        credentials: 'same-origin'
      }
    };
    const props = {
      rejectErrors: false,
      requestToken: () => Promise.resolve(refreshResult)
    };
    let firstRequest = true;
    fetchMock.get(fetchOpts.url, (url, opts) => {
      if (firstRequest) {
        firstRequest = false;
        return 401;
      }
      const { headers } = opts;
      return jsonResponse({ url, headers });
    });
    const result = await fetchWithRetry(fetchOpts.url, fetchOpts, props);
    expect(result.status).toEqual(200);
    const body = await result.json();
    const { headers } = body;
    expect(headers).toEqual({
      ...fetchOpts.headers,
      Authorization: `Bearer ${refreshResult.payload.accessToken}`
    });
  });

  it('handles failure to use refresh token', async () => {
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: vi.fn(),
      success: vi.fn(),
      failure: vi.fn(),
      rejectErrors: false,
      headers: {
        cache: "no-cache",
        credentials: 'same-origin'
      }
    };
    const refreshResult = {
      ok: false,
      status: 401,
      payload: {}
    };
    const props = {
      rejectErrors: false,
      requestToken: () => Promise.resolve(refreshResult)
    };
    fetchMock.get(fetchOpts.url, () => 401);
    log.setLevel('silent');
    const result = await fetchWithRetry(fetchOpts.url, fetchOpts, props);
    expect(result).toEqual({
      ok: false,
      error: '401: Failed to refresh access token'
    });
  });

  it('handles requesting a refresh token throwing an exception', async () => {
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: vi.fn(),
      success: vi.fn(),
      failure: vi.fn(),
      rejectErrors: true,
      headers: {
        cache: "no-cache",
        credentials: 'same-origin'
      }
    };
    const props = {
      rejectErrors: true,
      requestToken: () => Promise.reject('this is an error')
    };
    fetchMock.get(fetchOpts.url, () => 401);
    log.setLevel('silent');
    const err = await fetchWithRetry(fetchOpts.url, fetchOpts, props);
    expect(err).toEqual({
      error: 'this is an error',
      ok: false
    });
  });

  it('returns error on failure to use refresh token', async () => {
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: vi.fn(),
      success: vi.fn(),
      failure: vi.fn(),
      rejectErrors: false,
      headers: {
        cache: "no-cache",
        credentials: 'same-origin'
      }
    };
    const refreshResult = {
      ok: false,
      status: 401,
      payload: {}
    };
    const props = {
      rejectErrors: true,
      requestToken: () => Promise.resolve(refreshResult)
    };
    fetchMock.get(fetchOpts.url, () => 401);
    log.setLevel('silent');
    const err = await fetchWithRetry(fetchOpts.url, fetchOpts, props);
    expect(err).toEqual({
      error: '401: Failed to refresh access token',
      ok: false
    });
  });
});

describe('endpoints - receiveStream()', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('can process a multipart stream', async () => {
    const actions = [];
    const dispatch = (value) => actions.push(value);
    const textEnc = new TextEncoder();
    let num_parts = 0;
    const stream = {
      read: async () => {
        const done = (num_parts > 2);
        let body;
        if (!done) {
          body = `{"part": ${num_parts}}`;
          if (num_parts === 0) {
            body = `--boundary\r\n\r\n${body}\r\n\r\n`;
          }
          body = textEnc.encode(body);
        }
        num_parts++;
        return {
          done,
          value: {
            body
          }
        };
      }
    };
    await new Promise((resolve) => {
      const props = {
        success: (payload) => {
          if (payload.done === true) {
            resolve();
          }
          return {
            action: 'success',
            payload
          };
        }
      };
      receiveStream(stream, {}, dispatch, props);
    });
    const expected = [{
      action: "success",
      payload: {
        done: false,
        payload: {
          part: 0
        },
        timestamp: Date.now()
      }
    }, {
      action: "success",
      payload: {
        done: false,
        payload: {
          part: 1
        },
        timestamp: Date.now()
      }
    }, {
      action: "success",
      payload: {
        done: false,
        payload: {
          part: 2
        },
        timestamp: Date.now()
      }
    }, {
      action: "success",
      payload: {
        done: true,
        payload: {},
        timestamp: Date.now()
      }
    }];
    expect(actions).toEqual(expected);
  });
});

describe('endpoints - api', () => {
  describe('not logged in', () => {
    let dispatch, server, store;

    beforeEach(() => {
      server = new MockBingoServer(fetchMock);
      store = createStore(initialState);
      dispatch = store.dispatch;
    });

    afterEach(() => {
      server.shutdown();
    });

    it('check user', async () => {
      await expect(dispatch(api.getUserInfo({
        rejectErrors: false,
        before: userSlice.actions.requestUser,
        failure: userSlice.actions.failedFetchUser,
        success: userSlice.actions.receiveUser,
      }))).resolves.toMatchObject({
        payload: {
          error: '401: Unauthorized',
          method: 'GET',
          status: 401,
          url: '/api/user',
        },
      });
    });

    it('refresh access token using invalid refresh token', async () => {
      await expect(dispatch(refreshAccessToken('invalidRefreshToken'))).resolves.toMatchObject({
        headers: {
          Authorization: "Bearer invalidRefreshToken",
        },
        payload: {
          error: '401: Unauthorized',
          method: 'POST',
          status: 401,
          url: '/api/refresh',
        },
      });
    });

    it('logout', async () => {
      await expect(dispatch(api.logout())).resolves.toMatchObject({
        method: 'DELETE',
        payload: 'Logged out',
      });
    });

    it('registerUser', async () => {
      const username = 'username';
      const email = 'a.user@unit.test';
      const password = 'secret';
      await expect(dispatch(api.registerUser({
        body: {
          username,
          email,
          password
        },
        noAccessToken: true,
        rejectErrors: false,
      }))).resolves.toMatchObject({
        method: 'PUT',
        payload: {
          message: "Successfully registered",
          success: true,
          user: {
            username,
            email,
            groups: ['users'],
          }
        }
      });
    });

    it('checkUser', async () => {
      await expect(dispatch(api.checkUser({
        body: {
          username: 'username',
          email: 'a.user@unit.test'
        }
      }))).resolves.toMatchObject({
        method: 'POST',
        url: "/api/user/check",
        payload: {
          email: false,
          username: false,
        }
      });
    });

    it('passwordReset', async () => {
      await expect(dispatch(api.passwordReset({
        body: {
          email: 'a.user@unit.test'
        }
      }))).resolves.toMatchObject({
        method: 'POST',
        url: "/api/user/reset",
        payload: {
          email: 'a.user@unit.test',
          success: true,
        }
      });
    });

    it('checkGuestToken with missing token', async () => {
      await expect(dispatch(api.checkGuestToken({
        body: {},
        noAccessToken: true,
        rejectErrors: false,
      }))).resolves.toMatchObject({
        method: 'POST',
        url: "/api/user/guest",
        payload: {
          status: 400,
        }
      });
    });

    it('checkGuestToken', async () => {
      await expect(dispatch(api.checkGuestToken({
        body: {
          token: 'guest.token',
        },
        noAccessToken: true,
        rejectErrors: false,
      }))).resolves.toMatchObject({
        method: 'POST',
        url: "/api/user/guest",
        payload: {
          success: false,
        }
      });
    });

    it('getSettings', async () => {
      await expect(dispatch(api.getSettings())).resolves.toMatchObject({
        method: 'GET',
        url: '/api/settings',
        payload: {
          privacy: settings.privacy,
        }
      });
    });

    it('importGame', async () => {
      await expect(dispatch(api.importGame({
        body: {
          filename: 'gameTracks.json',
        },
      }))).resolves.toMatchObject({
        method: 'PUT',
        url: '/api/games',
        streaming: true,
        status: 401,
      });
    })
    it.each([
      ['getUserInfo', api.getUserInfo],
      ['modifyMyself', () => api.modifyMyself({ body: {} })],
      ['getGuestLinks', api.getGuestLinks],
      ['createGuestToken', api.createGuestToken],
      ['deleteGuestToken', () => api.deleteGuestToken({ token: 'guestToken' })],
      ['getUsersList', api.getUsersList],
      ['modifyUsers', api.modifyUsers],
      ['getGamesList', api.getGamesList],
      ['getGameDetail', () => api.getGameDetail({ gamePk: 43 })],
      ['modifyGame', () => api.modifyGame({ gamePk: 42 })],
      ['deleteGame', () => api.deleteGame({ gamePk: 42 })],
      ['exportGame', () => api.exportGame({ gamePk: 42 })],
      ['claimCard', () => api.claimCard({ gamePk: 23, ticketPk: 45 })],
      ['releaseCard', () => api.releaseCard({ gamePk: 23, ticketPk: 45 })],
      ['getTicketsList', () => api.getTicketsList({ gamePk: 43 })],
      ['getTicketsStatus', () => api.getTicketsStatus({ gamePk: 43 })],
      ['fetchCard', () => api.fetchCard({ gamePk: 23, ticketPk: 45 })],
      ['setCardCellChecked', () => api.setCardCellChecked({ gamePk: 12, ticketPk: 34, number: 5, checked: true })],
      ['downloadCard', () => api.claimCard({ gamePk: 23, ticketPk: 45 })],
      ['getDirectoryDetail', () => api.getDirectoryDetail({ dirPk: 12 })],
      ['getDirectoryList', api.getDirectoryList],
      ['searchForSongs', () => api.searchForSongs({ query: 'Pop', dirPk: 5 })],
      ['modifySettings', () => api.modifySettings({ body: [] })],
    ])('%s returns 401 status', async (_name, apiFn) => {
      await expect(dispatch(apiFn())).resolves.toMatchObject({
        payload: {
          error: '401: Unauthorized',
          status: 401,
        },
      });
    });
  });

  describe('logged in', () => {
    let dispatch, server, store, user;

    beforeEach(() => {
      server = new MockBingoServer(fetchMock, { currentUser: adminUser });
      user = server.getUserState(adminUser);
      store = createStore({
        ...initialState,
        user,
      });
      dispatch = store.dispatch;
    });

    afterEach(() => {
      server.shutdown();
    });

    it('getSettings', async () => {
      await expect(dispatch(api.getSettings())).resolves.toMatchObject({
        method: 'GET',
        url: '/api/settings',
        payload: settings,
      });
    });

    it('check user', async () => {
      const result = await dispatch(api.getUserInfo({
        rejectErrors: false,
        before: userSlice.actions.requestUser,
        failure: userSlice.actions.failedFetchUser,
        success: userSlice.actions.receiveUser,
      }));
      const currentUser = server.getUserState(user);
      expect(result).toMatchObject({
        method: 'GET',
        headers: {
          Authorization: `Bearer ${user.accessToken}`,
          cache: "no-cache",
          credentials: "same-origin",
        },
        payload: {
          ...adminUser,
          accessToken: currentUser.accessToken,
          refreshToken: currentUser.refreshToken,
        },
      });
    });

    it('logout', async () => {
      await expect(dispatch(api.logout())).resolves.toMatchObject({
        method: 'DELETE',
        payload: 'Logged out',
      });
    });

  });
});