import React from 'react';
import log from 'loglevel';

import { fetchMock, renderWithProviders } from '../../../tests';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { initialState } from '../../store/initialState';

import { PastGamesPopularityPage } from './PastGamesPopularityPage';

describe('PastGamesPopularityPage component', () => {
  let mockServer, user;
  beforeEach(() => {
    mockServer = new MockBingoServer(fetchMock, { loggedIn: true });
    user = mockServer.getUserState(normalUser);
  });

  afterEach(() => {
    mockServer.shutdown();
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to render graph of theme popularity previous games', async () => {
    const preloadedState = {
      ...initialState,
      user
    };
    const { asFragment, findAllByText } = renderWithProviders(
      <PastGamesPopularityPage />, { preloadedState });
    await findAllByText("Rock & Power Ballads", { exact: false });
    expect(asFragment()).toMatchSnapshot();
  });

  it('will rotate between vertical and horizontal', async () => {
    const preloadedState = {
      ...initialState,
      user
    };
    const { events, findByTestId, findAllByText } = renderWithProviders(
      <PastGamesPopularityPage />, { preloadedState });
    await findAllByText("Rock & Power Ballads", { exact: false });
    await findByTestId("vert-popularity-graph");
    await events.click(await findByTestId("rotate-button"));
    await findByTestId("horiz-popularity-graph");
  });
});