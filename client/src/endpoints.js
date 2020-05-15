export const apiServerURL = "/api";

/*
 make an API request and if the access token has expired,
 try to refresh the token and then retry the original request
*/
function fetchWithRetry(url, opts, requestToken) {
  return new Promise((resolve, reject) => {
    fetch(url, opts)
      .then(result => {
        if (result.ok || result.status !== 401 || !requestToken) {
          resolve(result);
          return;
        }
        requestToken()
          .then(refreshResult => {
            const { payload } = refreshResult;
            const { accessToken } = payload;
            opts.headers.Authorization = `Bearer ${accessToken}`;
            return fetch(url, opts).then(resolve);
          });
      })
      .catch(reject);
  });
}

const makeApiRequest = (props) => {
  const { method, url, before, success, failure } = props;
  let { body } = props;
  return (dispatch, getState) => {
    const state = getState();
    const { user } = state;
    const headers = {
      cache: "no-cache",
      credentials: 'same-origin',
      ...props.headers,
    };
    if (user.accessToken && props.noAccessToken !== true) {
      headers.Authorization = `Bearer ${user.accessToken}`;
     }
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
    const requestToken = (user.refreshToken && !props.noAccessToken) ? dispatchRequestToken : null;
    return fetchWithRetry(url, { method, headers, body }, requestToken)
      .then((response) => {
        if (!response.ok) {
          const result = {
            ...context,
            error: `${response.status}: ${response.statusText}`,
            status: response.status,
            statusText: response.statusText,
            timestamp: Date.now()
          };
          if (failure) {
            dispatch(failure(result));
          }
          dispatch(api.actions.networkError(result));
          return Promise.reject(result);
        }
        if (response.status === 200 && (!headers.Accept || headers.Accept === 'application/json')) {
          return response.json();
        }
        return response;
      })
      .then(payload => {
        if (payload.error) {
          const err = {
            ...context,
            timestamp: Date.now(),
            ...payload
          };
          if (failure) {
            dispatch(failure(err));
          }
          if (props.rejectErrors !== false) {
            return Promise.reject(err);
          }
        }
        const result = {
          ...context,
          payload,
          timestamp: Date.now()
        };
        if (success && !payload.error) {
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
  return (args) => makeApiRequest({ url, method, ...args });
}

export const api = {
  actions: {
    refreshAccessToken: () => Promise.reject('refreshAccessToken action not configured'),
    networkError: (context) => ({ type: 'NO-OP', payload: context }),
  },
  refreshToken: ({refreshToken, ...args}) => makeApiRequest({
    url: `${apiServerURL}/refresh`,
    method: 'POST',
    headers: {
      Authorization: `Bearer ${refreshToken}`
    },
    noAccessToken: true,
    ...args,
  }),
  login: restApi('POST', `${apiServerURL}/user`),
  getUserInfo: restApi('GET', `${apiServerURL}/user`),
  logout: restApi('DELETE', `${apiServerURL}/user`),
  registerUser: restApi('PUT', `${apiServerURL}/user`),
  checkUser: restApi('POST', `${apiServerURL}/user/check`),
  passwordReset: restApi('POST', `${apiServerURL}/user/reset`),
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
  claimCard: ({ gamePk, ticketPk, ...args }) => makeApiRequest({
    method: 'PUT',
    url: `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`,
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
};
