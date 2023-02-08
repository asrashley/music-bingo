import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ConnectedRouter } from 'connected-react-router';
import log from 'loglevel';

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
        {children}
      </ConnectedRouter>
    </Provider>);
  }
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}

const protectedRoutes = {
  '/api/user': true,
  '/api/settings': false,
};

export function installFetchMocks(fetchMock, {
  loggedIn = false,
  currentAccessToken = 1,
  refreshToken =  "refresh.token"
} = {}) {
  const apiRequest = async (url, opts) => {
    log.trace(`apiRequest ${url}`);
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
    if (url === '/api/user') {
      data['default'].refreshToken = refreshToken;
      data['default'].accessToken = accessToken();
    } else if (url === '/api/settings' && !loggedIn) {
      data['default'] = {
        privacy: data['default'].privacy
      };
    }
    const body = JSON.stringify(data['default']);
    return {
      body,
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': body.length
      }
    };
  };
  const accessToken = () => `access.token.${currentAccessToken}`;
  const refreshAccessToken = (url, opts) => {
    currentAccessToken++;
    console.log(`refreshAccessToken ${currentAccessToken}`);
    return {
      'accessToken': accessToken()
    };
  };
  const loginUser = async (url, opts) => {
    const { username, password } = JSON.parse(opts.body);
    if (username !== 'user' || password !== 'mysecret') {
      return 401;
    }
    const data = await import('./fixtures/user.json');
    data['default'].refreshToken = refreshToken;
    data['default'].accessToken = accessToken();
    loggedIn = true;
    const body = JSON.stringify(data['default']);
    return {
      body,
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': body.length
      }
    };
  };

  fetchMock.config.fallbackToNetwork = false;
  fetchMock.config.warnOnFallback = true;
  log.debug(`installFetchMocks ${loggedIn}`);
  fetchMock
    .post('/api/refresh', refreshAccessToken)
    .get('/api/games', apiRequest)
    .get('/api/user', apiRequest)
    .get('/api/settings', apiRequest)
    .post('/api/user', loginUser);
}
