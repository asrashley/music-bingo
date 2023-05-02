import React from 'react';

import { renderWithProviders } from '../testHelpers';
import { NavPanel } from './NavPanel';

import { initialState } from '../store/initialState';

import * as userData from '../fixtures/user.json';

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

  it('renders without throwing an exception', () => {
    const user = {
      ...userData['default'],
      groups: {
        "users": true, "creators": true, "hosts": true, "admin": true
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };
    const result = renderWithProviders(
      <NavPanel user={user} />, {
      preloadedState
    });
    result.findByText(user.username);
    result.findByText('githash');
    result.findByText('Clips');
  });

  it("doesn't include clips if not a creator", () => {
    const user = {
      ...userData['default'],
      groups: {
        "users": true, "creators": false, "hosts": true, "admin": false
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };

    const result = renderWithProviders(
      <NavPanel user={user} />, { preloadedState });
    result.findByText(user.username);
    result.findByText('githash');
    expect(result.queryByText('Clips')).toBe(null);
  });

  it('matches JSON snapshot', () => {
    const user = {
      ...userData['default'],
      groups: {
        "users": true
      },
      isFetching: false,
      registering: false,
      error: null,
      lastUpdated: 1675455186677,
      didInvalidate: false
    };
    const { asFragment } = renderWithProviders(
      <NavPanel user={user} />, { preloadedState });
    expect(asFragment()).toMatchSnapshot();
  });
});