import React from 'react';
import log from 'loglevel';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { PastGamesPopularityPage } from './PastGamesPopularityPage';

describe('PastGamesPopularityPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to render graph of theme popularity previous games', async () => {
    const { asFragment, findAllByText } = renderWithProviders(<PastGamesPopularityPage />);
    await findAllByText("Rock & Power Ballads", { exact: false });
    expect(asFragment()).toMatchSnapshot();
  });

  it('will rotate between vertical and horizontal', async () => {
    const { events, findByTestId, findAllByText } = renderWithProviders(<PastGamesPopularityPage />);
    await findAllByText("Rock & Power Ballads", { exact: false });
    await findByTestId("vert-popularity-graph");
    await events.click(await findByTestId("rotate-button"));
    await findByTestId("horiz-popularity-graph");
  });
});