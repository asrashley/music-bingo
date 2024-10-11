import React from 'react';
import { getByText } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';
import fetchMock from 'fetch-mock';

import { renderWithProviders } from '../../../tests';
import { MockBingoServer, normalUser } from '../../../tests/MockServer';
import { formatDuration } from '../../components/DateTime';
import { PastGamesPage } from './PastGamesPage';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import gameFixture from '../../../tests/fixtures/game/159.json';

describe('PastGamesPage component', () => {
  let user, apiMocks;
  beforeEach(() => {
    apiMocks = new MockBingoServer(fetchMock, { loggedIn: true });
    user = apiMocks.getUserState(normalUser);
  });

  afterEach(() => {
    apiMocks.shutdown();
    fetchMock.reset();
    log.resetLevel();
  });

  it('to render listing of previous games', async () => {
    const preloadedState = {
      ...initialState,
      user,
    };
    //log.setLevel('debug');
    const { asFragment, findAllByText, findByTestId, store } = renderWithProviders(
      <PastGamesPage />, { preloadedState });
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

  it('to render listing of previous games of a specific theme', async () => {
    const store = createStore({
      ...initialState,
      user,
      games: {
        ...initialState.games,
        games: {
          [gameFixture.pk]: {
            ...gameFixture,
            slug: 'rock',
            isFetchingDetail: false,
            invalidDetail: false,
            invalid: false,
          }
        },
        gameIds: {
          [gameFixture.id]: gameFixture.pk,
        },
        pastOrder: [
          gameFixture.pk,
        ],
        user: user.pk,
      },
      routes: {
        params: {
          slug: 'rock',
        },
      },
    });
    const { asFragment, findAllByText, getByText, getByTestId, queryByText } = renderWithProviders(
      <PastGamesPage />, { store });
    await findAllByText("20-06-01-2", { exact: false });
    getByText('Previous "Rock" Bingo games');
    const game = store.getState().games.games[84];
    game.tracks.forEach(track => {
      const tid = `track[${track.pk}]`;
      const dur = formatDuration(track.duration);
      expect(dur).not.toMatch(/N?aN?/);
      const row = getByTestId(tid);
      expect(row).toBeVisible();
      expect(row).toHaveClass(`${game.options.colour_scheme}-theme`);
      getByText(row, track.title);
      getByText(row, track.artist);
      getByText(row, track.album);
    });
    expect(queryByText("Rock & Power Ballads", { exact: false })).toBeNull();
    expect(asFragment()).toMatchSnapshot();
  });

  it('will reload data if "reload" button is clicked', async () => {
    const preloadedState = {
      ...initialState,
      user
    };
    const { events, getByText, findAllByText } = renderWithProviders(
      <PastGamesPage />, { preloadedState });
    await findAllByText("Rock & Power Ballads", { exact: false });
    expect(fetchMock.calls('/api/games', 'GET').length).toEqual(1);
    await events.click(getByText('Reload'));
    await waitForExpect(() => {
      expect(fetchMock.calls('/api/games', 'GET').length).toEqual(2);
    });
  });

  it('recommends guest user to upgrade to a registered account', async () => {
    const user = {
      ...initialState.user,
      groups: {
        guests: true,
      },
      guest: {
        valid: true,
        isFetching: false
      }
    };
    const preloadedState = {
      ...initialState,
      user,
    };

    const { findByText } = renderWithProviders(<PastGamesPage />, { preloadedState });
    await expect(findByText(
      'log out from this guest account and register an account',
      { exact: false })).resolves.toBeDefined();
  });
});