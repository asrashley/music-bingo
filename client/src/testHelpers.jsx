import { render, queries, buildQueries, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import PropTypes from 'prop-types';
import { ReduxRouter } from '@lagunovsky/redux-react-router';
import log from 'loglevel';
import { Readable } from "stream";
import userEvent from '@testing-library/user-event';
import { createMemoryHistory } from 'history';

import { DisplayDialog } from './components/DisplayDialog';
import { createStore } from './store/createStore';
import fetchMockHandlerTest from 'fetch-mock/esm/client';
import jestify from 'fetch-mock-jest/jestify';

import userData from './fixtures/user.json';

export const fetchMock = jestify(fetchMockHandlerTest);

/* custom query that looks for a "data-last-update" attribute in the container and compares that to
  the value provided to the query. It can be used to check if a component has been updated or
  to wait for it to re-render
  */
const queryAllByLastUpdate = (container, lastUpdate, options = {}) => {
  const { comparison } = {
    comparison: 'equals',
    ...options
  };
  log.trace(`queryAllByLastUpdate lastUpdate=${lastUpdate} comparison=${comparison} container="${container.nodeName}.${container.className}" ${container.id}`);
  return Array.from(container.querySelectorAll('[data-last-update]'))
    .filter((elt) => {
      const update = parseInt(elt.dataset.lastUpdate, 10);
      log.trace(`${elt.nodeName}.${elt.className} lastUpdate = ${update}`);
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
export const [queryByLastUpdate, getAllLastUpdate, getByLastUpdate, findAllLastUpdate, findByLastUpdate] = buildQueries(
  queryAllByLastUpdate,
  (container, selector) => `Found multiple elements from ${container} with last update selector: ${selector}`,
  (container, selector, opts = {}) => {
    const { comparison = 'equals' } = opts;
    return (`Unable to find an element from ${container.nodeName}.${container.className} with last update ${comparison} ${selector}`);
  }
);
const lastUpdatedQueries = { queryByLastUpdate, getAllLastUpdate, getByLastUpdate, findAllLastUpdate, findByLastUpdate };

/* custom query that uses a CSS selector to find elements */
const queryAllBySelector = (container, selector) => {
  log.trace(`queryAllBySelector ${selector}`);
  return Array.from(container.querySelectorAll(selector));
};
const [queryBySelector, getAllBySelector, getBySelector, findAllBySelector, findBySelector] = buildQueries(
  queryAllBySelector,
  (container, selector) => `Found multiple elements from ${container} with selector: ${selector}`,
  (container, selector) => `Unable to find an element from ${container} with selector: ${selector}`,
);
const bySelectorQueries = { queryBySelector, getAllBySelector, getBySelector, findAllBySelector, findBySelector };

const routerSelector = (state) => state.router

export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    history = createMemoryHistory(),
    store = createStore(preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (<Provider store={store}>
      <ReduxRouter history={history} routerSelector={routerSelector}>
        <DisplayDialog>
          {children}
        </DisplayDialog>
      </ReduxRouter>
    </Provider>);
  }
  Wrapper.propTypes = {
    children: PropTypes.node,
  };
  const events = userEvent.setup({
    delay: 10,
  });
  return {
    events,
    store,
    ...render(ui, {
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
}

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
  const refreshAccessToken = () => {
    currentAccessToken++;
    log.trace(`refreshAccessToken ${currentAccessToken}`);
    return {
      'accessToken': getAccessToken()
    };
  };
  const checkUser = async () => {
    log.debug(`checkUser loggedIn=${loggedIn}`);
    if (serverStatus !== null) {
      log.debug(`checkUser serverStatus=${serverStatus}`);
      return serverStatus;
    }
    if (!loggedIn) {
      return 401;
    }
    return jsonResponse({
      ...userData,
      refreshToken,
      accessToken: getAccessToken(),
    });
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
    let index = -1;
    let dbEntry;
    userDatabase.forEach((item, i) => {
      if (item.username === username && item.password === password) {
        dbEntry = item;
        index = i;
      }
    });
    log.debug(`loginUser: username="${username}" password="${password}" index=${index}`);
    if (!dbEntry) {
      return 401;
    }
    const user = {
      ...userData,
      pk: index + 2,
      ...dbEntry,
      refreshToken,
      accessToken: getAccessToken()
    };
    delete user.password;
    loggedIn = true;
    return jsonResponse(user);
  };
  const logoutUser = () => {
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
      log.trace(`checkIfUserExists status=${serverStatus}`);
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
  log.trace(`installFetchMocks ${loggedIn}`);
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
    logout: () => loggedIn = false,
    setResponseModifier: (url, fn) => {
      responseModifiers[url] = fn;
    },
    setServerStatus: (code) => {
      serverStatus = code;
    },
    jsonResponse
  };
}

export async function setFormFields(fields, events) {
  await Promise.all(fields.map(async ({ label, value, exact }) => {
    if (exact === undefined) {
      exact = true;
    }
    const elt = await screen.findByLabelText(label, { exact });
    if (events) {
      //await events.click(elt);
      await waitFor(() => events.clear(elt));
      /*
            await waitFor(() => events.clear(elt));
        await waitFor(() => events.type(elt, value));
      }*/
    }
    await waitFor(() => fireEvent.input(elt, {
      target: {
        value
      }
    }));
  }));
  const { label, exact, value } = fields[fields.length - 1];
  const elt = await screen.findByLabelText(label, { exact });
  await waitFor(() => {
    expect(elt.value).toBe(value);
  });
}

