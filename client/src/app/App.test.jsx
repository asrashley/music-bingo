import React from 'react';
import PropTypes from 'prop-types';
import { render, queries } from '@testing-library/react';
import { it } from 'vitest';
import { Provider } from 'react-redux';

import { installFetchMocks, fetchMock } from '../../tests';
import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import App from './App';


function renderWithProviders(ui) {
  const store = createStore(initialState);
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
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it('App component matches snapshot', async () => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(new Date('29 Dec 2023 19:12:00 GMT').getTime());
    const { asFragment, findByText } = renderWithProviders(<App />);
    await findByText('Privacy Policy');
    await findByText('admin');
    expect(asFragment()).toMatchSnapshot();
  });
})
