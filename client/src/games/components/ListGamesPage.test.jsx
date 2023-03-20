import React from 'react';
import { fireEvent, getByText, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { ListGamesPage } from './ListGamesPage';

describe('ListGamesPage component', () => {
  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('15 Feb 2022 03:12:00 GMT').getTime());
  });

  beforeEach(() => {
    const { setResponseModifier } = installFetchMocks(fetchMock, { loggedIn: true });
    setResponseModifier('/api/games', (url, data) => {
      return {
        past: [],
        games: data.past.map((game, idx) => {
          const start = Date.now() + idx * 60000;
          return {
            ...game,
            start: new Date(start).toISOString(),
            end: new Date(start + 30000).toISOString()
          };
        })
      };
    });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
  });

  afterAll(() => jest.useRealTimers());

  it('to render listing of current games', async () => {
    //log.setLevel('debug');
    const { asFragment, store } = renderWithProviders(<ListGamesPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    const game = store.getState().games.games[159];
    game.tracks.forEach(track => {
      const tid = `track[${track.pk}]`;
      const dur = formatDuration(track.duration);
      expect(dur).not.toMatch(/N?aN?/);
      const row = screen.getByTestId(tid);
      expect(row).toBeVisible();
      expect(row).toHaveClass(`${game.options.colour_scheme}-theme`);
      getByText(row, track.title);
      getByText(row, track.artist);
      getByText(row, track.album);
    });
    expect(asFragment()).toMatchSnapshot();
  });

  it('to show import game dialog', async () => {
    //log.setLevel('debug');
    renderWithProviders(<ListGamesPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    fireEvent.click(screen.getByText('Import Game'));
    await screen.findByText('Select a gameTracks.json file to import');
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
  });
});