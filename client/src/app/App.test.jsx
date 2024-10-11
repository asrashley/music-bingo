import React from 'react';
import PropTypes from 'prop-types';
import { render, queries, waitFor } from '@testing-library/react';
import { it } from 'vitest';
import { Provider } from 'react-redux';
import fetchMock from 'fetch-mock';

import { installFetchMocks } from '../../tests';
import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { adminUser } from '../../tests/MockServer';

import App from './App';

function renderWithProviders(ui, { preloadedState = initialState } = {}) {
  const store = createStore(preloadedState);
  function Wrapper({ children }) {
    return (<Provider store={store}>
      {children}
    </Provider>);
  }
  Wrapper.propTypes = {
    children: PropTypes.node.isRequired,
  };
  return {
    store, ...render(ui, {
      wrapper: Wrapper,
      queries,
    })
  };
}

describe('App', () => {
  let mockServer;

  beforeEach(() => {
    mockServer = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.reset();
    mockServer.shutdown();
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it('App component matches snapshot', async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('29 Dec 2023 19:12:00 GMT').getTime());
    const preloadedState = {
      ...initialState,
      user: mockServer.getUserState(adminUser),
    };
    const { asFragment, findByText } = renderWithProviders(<App />, { preloadedState });
    await findByText('Privacy Policy');
    await findByText('admin');
    await findByText('previous Bingo games', { exact: false });
    await findByText('Log out');
    await waitFor(async () => {
      await fetchMock.flush(true);
    });
    expect(asFragment()).toMatchSnapshot();
  });
})
