import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ConnectedRouter } from 'connected-react-router';
import log from 'loglevel';

import { DisplayDialog } from './components/DisplayDialog';
import { createStore } from './store/createStore';
import { history } from './store/history';

export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    store = createStore(preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (<Provider store={store}>
      <ConnectedRouter history={history}>
        <DisplayDialog>
          {children}
        </DisplayDialog>
      </ConnectedRouter>
    </Provider>);
  }
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

const protectedRoutes = {
  '/api/directory': true,
  '/api/game': true,
  '/api/settings': false,
  '/api/user': true,
};

export function installFetchMocks(fetchMock, {
  loggedIn = false,
  currentAccessToken = 1,
  refreshToken =  "refresh.token"
} = {}) {
  const responseModifiers = {};
  let serverStatus = null;
  const jsonResponse = (payload, status = 200) => {
    const body = JSON.stringify(payload);
    return {
      body,
      status,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': body.length
      }
    };
  };
  const apiRequest = async (url, opts) => {
    log.trace(`apiRequest ${url}`);
    if (serverStatus !== null) {
      return serverStatus;
    }
    if (protectedRoutes[url]) {
      const { headers } = opts;
      log.trace(`Authorization = headers?.Authorization`);
      const bearer = `Bearer ${accessToken()}`;
      if (headers?.Authorization !== bearer) {
        log.debug(`Invalid access token "${headers?.Authorization}" !== "${bearer}"`);
        return 401;
      }
    }
    const filename = url.replace(/^\/api/, './fixtures');
    log.trace(`load ${filename}`);
    const data = await import(`${filename}.json`);
    log.trace(`${filename} = ${Object.keys(data['default']).join(',')}`);
    if (url === '/api/settings' && !loggedIn) {
      data['default'] = {
        privacy: data['default'].privacy
      };
    }
    const modFn = responseModifiers[url];
    if (modFn !== undefined) {
      return jsonResponse(modFn(url, data['default']));
    }
    return jsonResponse(data['default']);
  };
  const accessToken = () => `access.token.${currentAccessToken}`;
  const refreshAccessToken = (url, opts) => {
    currentAccessToken++;
    log.trace(`refreshAccessToken ${currentAccessToken}`);
    return {
      'accessToken': accessToken()
    };
  };
  const checkUser = async (url, opts) => {
    log.trace(`checkUser ${loggedIn}`);
    if (serverStatus !== null) {
      return serverStatus;
    }
    if (!loggedIn) {
      return 401;
    }
    const data = await import('./fixtures/user.json');
    data['default'].refreshToken = refreshToken;
    data['default'].accessToken = accessToken();
    return jsonResponse(data['default']);
  };
  const loginUser = async (url, opts) => {
    log.trace('loginUser');
    if (serverStatus !== null) {
      return serverStatus;
    }
    const { username, password } = JSON.parse(opts.body);
    if (username !== 'user' || password !== 'mysecret') {
      return 401;
    }
    const data = await import('./fixtures/user.json');
    data['default'].refreshToken = refreshToken;
    data['default'].accessToken = accessToken();
    loggedIn = true;
    return jsonResponse(data['default']);
  };
  const logoutUser = (url, opts) => {
    if (serverStatus !== null) {
      log.trace(`logoutUser status={serverStatus}`);
      return serverStatus;
    }
    log.trace('logoutUser');
    loggedIn = false;
    return jsonResponse('Logged out');
  };

  fetchMock.config.fallbackToNetwork = false;
  fetchMock.config.warnOnFallback = true;
  log.debug(`installFetchMocks ${loggedIn}`);
  fetchMock
    .get('/api/directory', apiRequest)
    .get(/api\/directory\/\d+/, apiRequest)
    .get('/api/games', apiRequest)
    .get(/api\/game\/\d+/, apiRequest)
    .post('/api/refresh', refreshAccessToken)
    .get('/api/settings', apiRequest)
    .get('/api/user', checkUser)
    .post('/api/user', loginUser)
    .delete('/api/user', logoutUser)
    .get('/api/users', apiRequest)
    .get('/api/user/guest', apiRequest);

  return {
    getAccessToken: accessToken,
    isLoggedIn: () => loggedIn,
    setResponseModifier: (url, fn) => {
      responseModifiers[url] = fn;
    },
    setServerStatus: (code) => {
      serverStatus = code;
    },
    jsonResponse
  };
}
