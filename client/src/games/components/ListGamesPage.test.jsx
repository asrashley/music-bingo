import React from 'react';
import { getByText } from '@testing-library/react';
import log from 'loglevel';

import { ListGamesPage } from './ListGamesPage';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { formatDuration } from '../../components/DateTime';
import { initialState } from '../../store';
import user from '../../../tests/fixtures/userState.json';

describe('ListGamesPage component', () => {
  const preloadedState = {
    ...initialState,
    user,
  };

  beforeEach(() => {
    const { setResponseModifier } = installFetchMocks(fetchMock, { loggedIn: true });
    setResponseModifier('/api/games', (_url, data) => {
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
    vi.useRealTimers();
  });

  it('to render listing of current games', async () => {
    //log.setLevel('debug');
    vi.useFakeTimers();
    vi.setSystemTime(new Date('15 Feb 2022 03:12:00 GMT').getTime());
    const { asFragment, findAllByText, findByTestId, store } = renderWithProviders(
      <ListGamesPage />, { preloadedState });
    await findAllByText("Rock & Power Ballads", { exact: false });
    const game = store.getState().games.games[159];
    await Promise.all(game.tracks.map(async (track) => {
      const tid = `track[${track.pk}]`;
      const dur = formatDuration(track.duration);
      expect(dur).not.toMatch(/N?aN?/);
      const row = await findByTestId(tid);
      expect(row).toBeVisible();
      expect(row).toHaveClass(`${game.options.colour_scheme}-theme`);
      getByText(row, track.title);
      getByText(row, track.artist);
      getByText(row, track.album);
    }));
    expect(asFragment()).toMatchSnapshot();
  });

  it('to show import game dialog', async () => {
    const { events, getByText, findAllByText, findByText, getByRole } = renderWithProviders(
      <ListGamesPage />, { preloadedState });
    await findAllByText("Rock & Power Ballads", { exact: false });
    await events.click(getByText('Import Game'));
    await findByText('Select a gameTracks.json file to import');
    await events.click(getByRole('button', { name: 'Cancel' }));
  });
});