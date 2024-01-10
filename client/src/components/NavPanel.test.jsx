import React from 'react';

import { renderWithProviders } from '../../tests';
import { NavPanel } from './NavPanel';

import { initialState } from '../store/initialState';
import { createStore } from '../store/createStore';

import userData from '../../tests/fixtures/userState.json';

describe('NavPanel component', () => {

  const buildInfo = {
    branch: 'main',
    buildDate: 'Mon Feb 13 20:41:03 2023 +0000',
    tags: 'tags',
    version: '1.2.3',
    commit: {
      hash: '914af0ce5972379b108d54f78e3162fdbb8551a1',
      shortHash: '914af0ce5'
    }
  };
  const preloadedState = {
    ...initialState,
    system: {
      ...initialState.system,
      invalid: false,
      error: null,
      lastUpdated: 1675455186677,
      buildInfo
    }
  };

  it('renders without throwing an exception', async () => {
    const user = {
      ...userData,
      groups: {
        "users": true, "creators": true, "hosts": true, "admin": true
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };
    const store = createStore({
      ...preloadedState,
      user,
    });
    const { findByText } = renderWithProviders(<NavPanel />, { store });
    await findByText(user.username);
    await findByText(buildInfo.commit.shortHash);
    await findByText('Clips');
  });

  it('renders correctly when user not logged in', () => {
    const { getByText } = renderWithProviders(<NavPanel />);
    getByText('Log in');
  });

  it("doesn't include clips if not a creator", async () => {
    const user = {
      ...userData,
      groups: {
        "users": true, "creators": false, "hosts": true, "admin": false
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };
    const store = createStore({
      ...preloadedState,
      user,
    });

    const { findByText, queryByText } = renderWithProviders(<NavPanel />, { store });
    await findByText(user.username);
    await findByText(buildInfo.commit.shortHash);
    expect(queryByText('Clips')).not.toBeInTheDocument();
  });

  it('matches JSON snapshot', async () => {
    const user = {
      ...userData,
      groups: {
        users: true,
        admin: true,
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };
    const store = createStore({
      ...preloadedState,
      user,
    });
    const { asFragment, findByText } = renderWithProviders(<NavPanel />, { store });
    await findByText(user.username);
    await findByText(buildInfo.commit.shortHash);
    expect(asFragment()).toMatchSnapshot();
  });
});