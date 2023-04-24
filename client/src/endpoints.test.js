import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { fetchWithRetry, receiveStream } from './endpoints';
import { jsonResponse } from './testHelpers';

describe('endpoints', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
  });

  afterEach(() => {
    jest.useRealTimers();
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
      before: jest.fn(),
      success: jest.fn(),
      failure: jest.fn(),
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
      before: jest.fn(),
      success: jest.fn(),
      failure: jest.fn(),
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
    fetchMock.get(fetchOpts.url, (url, opts) => {
      return 401;
    });
    log.setLevel('silent');
    const result = await fetchWithRetry(fetchOpts.url, fetchOpts, props);
    expect(result).toEqual({
      ok: false,
      error: '401: Failed to refresh access token'
    });
  });

  it('handles requesting a refresh token throwing an exception', (done) => {
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: jest.fn(),
      success: jest.fn(),
      failure: jest.fn(),
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
    fetchMock.get(fetchOpts.url, (url, opts) => {
      return 401;
    });
    log.setLevel('silent');
    fetchWithRetry(fetchOpts.url, fetchOpts, props)
      .then(() => done("fetchWithRetry should have thrown an exception"))
      .catch(err => {
        expect(err).toEqual('this is an error');
        done();
      });
  });

  it('throws exception on failure to use refresh token', (done) => {
    const fetchOpts = {
      method: 'GET',
      url: '/api/test',
      before: jest.fn(),
      success: jest.fn(),
      failure: jest.fn(),
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
    fetchMock.get(fetchOpts.url, (url, opts) => {
      return 401;
    });
    log.setLevel('silent');
    fetchWithRetry(fetchOpts.url, fetchOpts, props)
      .then(() => done("fetchWithRetry should have thrown an exception"))
      .catch(err => {
        expect(err).toEqual('401: Failed to refresh access token');
        done();
      });
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