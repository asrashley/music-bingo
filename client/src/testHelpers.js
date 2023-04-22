import { render, queries, buildQueries } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ConnectedRouter } from 'connected-react-router';
import log from 'loglevel';
import { screen, fireEvent } from '@testing-library/react';
import waitForExpect from 'wait-for-expect';
import { Readable } from "stream";

import { DisplayDialog } from './components/DisplayDialog';
import { createStore } from './store/createStore';
import { history } from './store/history';

/* custom query that looks for a "data-last-update" attribute in the container and compares that to
  the value provided to the query. It can be used to check if a component has been updated or
  to wait for it to re-render
  */
const queryAllByLastUpdate = (_, container, lastUpdate, options = {}) => {
  const { comparison } = {
    comparison: 'equals',
    ...options
  };
  log.debug(`queryAllByLastUpdate lastUpdate=${lastUpdate} comparison=${comparison}`);
  return Array.from(container.querySelectorAll('[data-last-update]'))
    .filter((elt) => {
      const update = parseInt(elt.dataset.lastUpdate, 10);
      log.trace(`elt.lastUpdate = ${update}`);
      if (isNaN(update)) {
        return false;
      }
      switch (comparison) {
        case 'equals':
          return update === lastUpdate;
        case 'greaterThan':
          return update > lastUpdate;
        case 'greaterThanOrEquals':
          return update >= lastUpdate;
        case 'lessThan':
          return update < lastUpdate;
        case 'lessThanOrEquals':
          return update <= lastUpdate;
        default:
          return true;
      }
    });
};
const [queryByLastUpdate, getAllLastUpdate, getByLastUpdate, findAllLastUpdate, findByLastUpdate] = buildQueries(
  queryAllByLastUpdate,
  (container, selector) => `Found multiple elements from ${container} with last update selector: ${selector} ${selector.innerHTML}`,
  (container, selector) => `Unable to find an element from ${container} with last update selector: ${selector}`,
);
const lastUpdatedQueries = { queryByLastUpdate, getAllLastUpdate, getByLastUpdate, findAllLastUpdate, findByLastUpdate };

/* custom query that uses a CSS selector to find elements */
const queryAllBySelector = (_, container, selector) => {
  log.debug(`queryAllBySelector ${selector}`);
  return Array.from(container.querySelectorAll(selector));
};
const [queryBySelector, getAllBySelector, getBySelector, findAllBySelector, findByBySelector] = buildQueries(
  queryAllBySelector,
  (container, selector) => `Found multiple elements from ${container} with selector: ${selector}`,
  (container, selector) => `Unable to find an element from ${container} with selector: ${selector}`,
);
const bySelectorQueries = { queryBySelector, getAllBySelector, getBySelector, findAllBySelector, findByBySelector };

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
  return {
    store, ...render(ui, {
      wrapper: Wrapper,
      queries: {
        ...queries,
        ...lastUpdatedQueries,
        ...bySelectorQueries
      },
      ...renderOptions
    })
  };
}

const protectedRoutes = {
  '/api/directory': true,
  '/api/game': true,
  '/api/settings': false,
  '/api/user': true,
};

export function jsonResponse(payload, status = 200) {
  const body = JSON.stringify(payload);
  return {
    body,
    status,
    headers: {
      'Cache-Control': 'max-age = 0, no_cache, no_store, must_revalidate',
      'Content-Type': 'application/json',
      'Content-Length': body.length
    }
  };
};

export class MockResponse extends Response {
  constructor(...args) {
    if (args[0] instanceof ReadableStream) {
      args[0] = Readable.from(args[0]);
    }
    super(...args);
  }
}

export function installFetchMocks(fetchMock, {
  loggedIn = false,
  currentAccessToken = 1,
  refreshToken = "refresh.token"
} = {}) {
  const responseModifiers = {};
  let serverStatus = null;
  const apiRequest = async (url, opts) => {
    log.trace(`apiRequest ${url}`);
    if (serverStatus !== null) {
      return serverStatus;
    }
    if (protectedRoutes[url]) {
      const { headers } = opts;
      log.trace(`Authorization = headers?.Authorization`);
      const bearer = `Bearer ${getAccessToken()}`;
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
    let responsePayload = data['default'];
    if (modFn !== undefined) {
      log.debug(`modify response for ${url}`);
      responsePayload = modFn(url, responsePayload);
      log.debug(`modify response for ${url} done`);
    }
    return jsonResponse(responsePayload);
  };
  const getAccessToken = () => `access.token.${currentAccessToken}`;
  const refreshAccessToken = (url, opts) => {
    currentAccessToken++;
    log.trace(`refreshAccessToken ${currentAccessToken}`);
    return {
      'accessToken': getAccessToken()
    };
  };
  const checkUser = async (url, opts) => {
    log.debug(`checkUser loggedIn=${loggedIn}`);
    if (serverStatus !== null) {
      log.debug(`checkUser serverStatus=${serverStatus}`);
      return serverStatus;
    }
    if (!loggedIn) {
      return 401;
    }
    const data = await import('./fixtures/user.json');
    data['default'].refreshToken = refreshToken;
    data['default'].accessToken = getAccessToken();
    return jsonResponse(data['default']);
  };
  const userDatabase = [{
    username: 'user',
    email: 'a.user@example.tld',
    password: 'mysecret'
  }];
  const loginUser = async (url, opts) => {
    if (serverStatus !== null) {
      log.debug(`loginUser status=${serverStatus}`);
      return serverStatus;
    }
    const { username, password } = JSON.parse(opts.body);
    const userIsValid = userDatabase.some(item => (
      item.username === username && item.password === password));
    log.debug(`loginUser: username="${username}" password="${password}" valid=${userIsValid}`);
    if (!userIsValid) {
      return 401;
    }
    const data = await import('./fixtures/user.json');
    data['default'].refreshToken = refreshToken;
    data['default'].accessToken = getAccessToken();
    loggedIn = true;
    return jsonResponse(data['default']);
  };
  const logoutUser = (url, opts) => {
    if (serverStatus !== null) {
      log.trace(`logoutUser status=${serverStatus}`);
      return serverStatus;
    }
    log.trace('logoutUser');
    loggedIn = false;
    return jsonResponse('Logged out');
  };
  const checkIfUserExists = (url, opts) => {
    if (serverStatus !== null) {
      log.debug(`checkIfUserExists status=${serverStatus}`);
      return serverStatus;
    }
    const { username, email } = JSON.parse(opts.body);
    const response = {
      "username": false,
      "email": false
    };
    userDatabase.forEach((item) => {
      if (item.username === username) {
        response.username = true;
      }
      if (item.email === email) {
        response.email = true;
      }
    });
    log.debug(`checkIfUserExists username=${username} email=${email} response=${JSON.stringify(response)}`);
    return jsonResponse(response);
  };

  Object.assign(fetchMock.config, {
    fallbackToNetwork: false,
    warnOnFallback: true,
    Response: MockResponse,
  });
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
    .post('/api/user/check', checkIfUserExists)
    .get('/api/users', apiRequest)
    .get('/api/user/guest', apiRequest);

  return {
    getAccessToken,
    getRefreshToken: () => refreshToken,
    isLoggedIn: () => loggedIn,
    addUser: (user) => userDatabase.push(user),
    setResponseModifier: (url, fn) => {
      responseModifiers[url] = fn;
    },
    setServerStatus: (code) => {
      serverStatus = code;
    },
    jsonResponse
  };
}

export async function setFormFields(fields) {
  fields.forEach(({ label, value, exact }) => {
    if (exact === undefined) {
      exact = true;
    }
    fireEvent.input(screen.getByLabelText(label, { exact }), {
      target: {
        value
      }
    });
  });
  await waitForExpect(() => {
    const last = fields[fields.length - 1];
    const { value } = document.querySelector(`input[name="${last.label}"`);
    expect(value).toBe(fields[fields.length - 1].value);
  });
}

