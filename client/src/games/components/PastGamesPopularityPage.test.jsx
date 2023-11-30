import React from 'react';
import { screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { PastGamesPopularityPage } from './PastGamesPopularityPage';

describe('PastGamesPopularityPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });
  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to render table of theme popularity previous games', async () => {
    //log.setLevel('debug');
    const { asFragment } = renderWithProviders(<PastGamesPopularityPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    expect(asFragment()).toMatchSnapshot();
  });
});