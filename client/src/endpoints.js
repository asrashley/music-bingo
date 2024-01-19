import multipartStream from '@asrashley/multipart-stream';
import log from 'loglevel';

export const apiServerURL = "/api";

/*
 make an API request and if the access token has expired,
 try to refresh the token and then retry the original request
*/
export async function fetchWithRetry(url, opts, props) {
  const { requestToken } = props;
  log.debug(`fetch ${opts.method} ${url}`);
  try {
    const result = await fetch(url, opts);
    log.debug(`${opts.method} ${url} ok=${result.ok} status=${result.status} statusText=${result.statusText}`);
    if (result.ok || result.status !== 401 || !requestToken) {
      return result;
    }
    log.debug('Trying to refresh access token');
    const refreshResult = await requestToken();
    const { ok, status = "Unknown error", payload = {} } = refreshResult;
    const { accessToken } = payload;
    if (ok === false || !accessToken) {
      log.debug('Failed to refresh access token');
      return {
        ok: false,
        error: `${status}: Failed to refresh access token`,
      };
    }
    opts.headers.Authorization = `Bearer ${accessToken}`;
    log.debug(`retry fetch with bearer token ${opts.method} ${url}`);
    return await fetch(url, opts);
  } catch (err) {
    log.error(`fetch of ${url} failed ${err}`);
    log.error(err);
    return {
      ok: false,
      error: `${err}`
    };
  }
}

export function receiveStream(stream, context, dispatch, props) {
  const { success } = props;
  const processChunk = ({ done, value }) => {
    const headers = props.headers || {};
    if (!done && (!headers.Accept || headers.Accept === 'application/json')) {
      let string = new TextDecoder("utf-8").decode(value.body);
      if (string.startsWith("--")) {
        /* Fetch has returned complete HTTP multi-part part */
        const split = string.split('\r\n\r\n', 2);
        string = split[1];
      }
      value = JSON.parse(string);
    }
    const result = {
      ...context,
      done,
      payload: value,
      timestamp: Date.now()
    };
    if (Array.isArray(success)) {
      success.forEach(action => dispatch(action(result)));
    } else {
      dispatch(success(result));
    }
    if (!done) {
      stream.read().then(processChunk);
    }
  };
  stream.read().then(processChunk);
}

const makeApiRequest = (props) => {
  const { method = "GET", url, before, success, failure } = props;
  return (dispatch, getState) => {
    const { user } = getState();
    const headers = {
      cache: "no-cache",
      credentials: 'same-origin',
      ...props.headers,
    };
    if (user.accessToken && props.noAccessToken !== true) {
      headers.Authorization = `Bearer ${user.accessToken}`;
    }
    let { body } = props;
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
      if (typeof (body) === 'object') {
        body = JSON.stringify(body);
      }
    }
    const context = { url, method, body, user, headers };
    for (let key in props) {
      const value = props[key];
      if (typeof (value) !== 'function' && key !== 'success') {
        context[key] = value;
      }
    }
    if (before !== undefined) {
      dispatch(before(context));
    }
    const dispatchRequestToken = () =>
      dispatch(api.actions.refreshAccessToken(user.refreshToken));
    const requestToken = (user.refreshToken && props.noAccessToken !== false) ? dispatchRequestToken : null;
    return fetchWithRetry(url, { method, headers, body }, { requestToken })
      .then((response) => {
        log.trace(`url=${url} ok=${response.ok} status=${response.status} statusText=${response.statusText}`);
        if (!response.ok) {
          const { status, statusText } = response;
          const { error = `${status}: ${statusText}` } = response;
          const result = {
            ...context,
            error,
            status,
            statusText,
            timestamp: Date.now()
          };
          if (failure) {
            dispatch(failure(result));
          }
          dispatch(api.actions.networkError(result));
          return (result);
        }
        if (response.status === 200 && props.streaming === true) {
          return multipartStream(response.headers.get('Content-Type'),
            response.body).getReader();
        }
        const okStatus = response.status >= 200 && response.status <= 299;
        if (okStatus && props.parseResponse !== false &&
          (!headers.Accept || headers.Accept === 'application/json')) {
          return response.json();
        }
        return response;
      })
      .then(payload => {
        if (props.streaming === true) {
          if (success) {
            receiveStream(payload, context, dispatch, props);
          }
          return payload;
        }
        if (payload.error) {
          log.trace(`payload indicates error: ${payload.error}`);
          const err = {
            ...context,
            timestamp: Date.now(),
            ...payload
          };
          if (failure) {
            dispatch(failure(err));
          }
        }
        const result = {
          ...context,
          payload,
          timestamp: Date.now()
        };
        if (success && !payload.error) {
          log.trace(`API request success ${method} ${url} ${result.timestamp}`);
          if (Array.isArray(success)) {
            success.forEach(action => dispatch(action(result)));
          } else {
            dispatch(success(result));
          }
        }
        return result;
      });
  };
};

function restApi(method, url) {
  return (args) => makeApiRequest({
    url,
    method,
    rejectErrors: false,
    ...args
  });
}

export const api = {
  actions: {
    refreshAccessToken: () => Promise.reject('refreshAccessToken action not configured'),
    networkError: (context) => ({ type: 'NO-OP', payload: context }),
  },
  refreshToken: ({ refreshToken, ...args }) => makeApiRequest({
    url: `${apiServerURL}/refresh`,
    method: 'POST',
    headers: {
      Authorization: `Bearer ${refreshToken}`
    },
    noAccessToken: true,
    rejectErrors: false,
    ...args,
  }),
  exportDatabase: (args) => makeApiRequest({
    ...args,
    method: 'GET',
    headers: {
      Accept: "application/json",
    },
    parseResponse: false,
    url: `${apiServerURL}/database`,
  }),
  importDatabase: (args) => makeApiRequest({
    ...args,
    method: 'PUT',
    url: `${apiServerURL}/database`,
    streaming: true,
  }),
  login: restApi('POST', `${apiServerURL}/user`),
  getUserInfo: restApi('GET', `${apiServerURL}/user`),
  logout: restApi('DELETE', `${apiServerURL}/user`),
  registerUser: restApi('PUT', `${apiServerURL}/user`),
  checkUser: restApi('POST', `${apiServerURL}/user/check`),
  passwordReset: restApi('POST', `${apiServerURL}/user/reset`),
  modifyMyself: restApi('POST', `${apiServerURL}/user/modify`),
  checkGuestToken: restApi('POST', `${apiServerURL}/user/guest`),
  createGuestAccount: restApi('PUT', `${apiServerURL}/user/guest`),
  getGuestLinks: restApi('GET', `${apiServerURL}/user/guest`),
  createGuestToken: restApi('PUT', `${apiServerURL}/user/guest/add`),
  deleteGuestToken: ({ token, ...args }) => makeApiRequest({
    method: 'DELETE',
    url: `${apiServerURL}/user/guest/delete/${token}`,
    token,
    ...args
  }),
  getUsersList: restApi('GET', `${apiServerURL}/users`),
  modifyUsers: restApi('POST', `${apiServerURL}/users`),
  getGamesList: restApi('GET', `${apiServerURL}/games`),
  getGameDetail: ({ gamePk, ...args }) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/game/${gamePk}`,
    gamePk,
    ...args
  }),
  modifyGame: ({ gamePk, ...args }) => makeApiRequest({
    method: 'POST',
    url: `${apiServerURL}/game/${gamePk}`,
    gamePk,
    ...args
  }),
  deleteGame: (args) => makeApiRequest({
    ...args,
    method: 'DELETE',
    url: `${apiServerURL}/game/${args.gamePk}`,
  }),
  exportGame: (args) => makeApiRequest({
    ...args,
    method: 'GET',
    headers: {
      Accept: "application/json",
    },
    parseResponse: false,
    url: `${apiServerURL}/game/${args.gamePk}/export`,
  }),
  importGame: (args) => makeApiRequest({
    ...args,
    method: 'PUT',
    url: `${apiServerURL}/games`,
    streaming: true,
  }),
  claimCard: ({ gamePk, ticketPk, ...args }) => makeApiRequest({
    method: 'PUT',
    url: `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`,
    rejectErrors: false,
    gamePk,
    ticketPk,
    ...args
  }),
  releaseCard: ({ gamePk, ticketPk, ...args }) => makeApiRequest({
    method: 'DELETE',
    url: `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`,
    gamePk,
    ticketPk,
    ...args
  }),
  getTicketsList: ({ gamePk, ...args }) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/game/${gamePk}/tickets`,
    gamePk,
    ...args
  }),
  getTicketsStatus: ({ gamePk, ...args }) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/game/${gamePk}/status`,
    gamePk,
    ...args
  }),
  fetchCard: ({ gamePk, ticketPk, ...args }) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`,
    gamePk,
    ticketPk,
    ...args
  }),
  setCardCellChecked: ({ gamePk, ticketPk, number, checked, ...args }) => makeApiRequest({
    method: (checked ? 'PUT' : 'DELETE'),
    url: `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}/cell/${number}`,
    gamePk, ticketPk, number, checked, ...args,
  }),
  downloadCard: (args) => makeApiRequest({
    ...args,
    method: 'GET',
    url: `${apiServerURL}/game/${args.gamePk}/ticket/ticket-${args.ticketPk}.pdf`,
    headers: {
      Accept: "application/pdf",
    }
  }),
  getDirectoryDetail: ({ dirPk, ...args }) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/directory/${dirPk}`,
    dirPk, ...args
  }),
  getDirectoryList: (args) => makeApiRequest({
    method: 'GET',
    url: `${apiServerURL}/directory`,
    ...args
  }),
  searchForSongs: ({ query, dirPk, ...args }) => makeApiRequest({
    method: 'GET',
    url: dirPk ? `${apiServerURL}/song/${dirPk}?q=${query}` : `${apiServerURL}/song?q=${query}`,
    dirPk,
    query,
    ...args
  }),
  getSettings: restApi('GET', `${apiServerURL}/settings`),
  modifySettings: restApi('POST', `${apiServerURL}/settings`),
};
