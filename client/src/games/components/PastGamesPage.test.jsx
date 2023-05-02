import React from 'react';
import { getByText, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { PastGamesPage } from './PastGamesPage';

describe('PastGamesPage component', () => {
  beforeEach(() => {
    installFetchMocks(fetchMock, { loggedIn: true });
  });
  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  it('to render listing of previous games', async () => {
    //log.setLevel('debug');
    const { asFragment, store } = renderWithProviders(<PastGamesPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    const game = store.getState().games.games[159];
    game.tracks.forEach(track => {
      const tid = `track[${track.pk}]`;
      const dur = formatDuration(track.duration);
      expect('dur').not.toMatch(/N?aN?/);
      const row = screen.getByTestId(tid);
      expect(row).toBeVisible();
      expect(row).toHaveClass(`${game.options.colour_scheme}-theme`);
      getByText(row, track.title);
      getByText(row, track.artist);
      getByText(row, track.album);
    });
    expect(asFragment()).toMatchSnapshot();
  });
});