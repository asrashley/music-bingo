import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { PastGamesPopularityPage } from './PastGamesPopularityPage';

describe('PastGamesPopularityPage component', () => {
  let apiMocks;

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to render graph of theme popularity previous games', async () => {
    //log.setLevel('debug');
    const { asFragment } = renderWithProviders(<PastGamesPopularityPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    expect(asFragment()).toMatchSnapshot();
  });

  it('will reload data if "reload" button is clicked', async () => {
    const fetchGamesSpy = jest.fn((_, data) => data);
    apiMocks.setResponseModifier('/api/games', fetchGamesSpy);
    const { getByText } = renderWithProviders(<PastGamesPopularityPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    expect(fetchGamesSpy).toHaveBeenCalledTimes(1);
    fireEvent.click(getByText('Reload'));
    await waitForExpect(() => {
      expect(fetchGamesSpy).toHaveBeenCalledTimes(2);
    });
  });

  it('will rotate between vertical and horizontal', async () => {
    const { getByTestId } = renderWithProviders(<PastGamesPopularityPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    getByTestId("vert-popularity-graph");
    fireEvent.click(getByTestId("rotate-button"));
    await screen.getByTestId("horiz-popularity-graph");
  });
});