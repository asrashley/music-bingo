import React from 'react';
import { fireEvent, getByText, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";
import waitForExpect from 'wait-for-expect';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { PastGamesPage } from './PastGamesPage';
import { initialState } from '../../store/initialState';

describe('PastGamesPage component', () => {
  let apiMocks;

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
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

  it('to render listing of previous games of a specific theme', async () => {
    //log.setLevel('debug');
    const location = {
      params: {
        slug: "rock"
      }
    };
    const { asFragment, store } = renderWithProviders(<PastGamesPage match={location} />);
    await screen.findAllByText("20-06-01-2", { exact: false });
    screen.getByText('Previous "Rock" Bingo games');
    const game = store.getState().games.games[84];
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
    expect(screen.queryByText("Rock & Power Ballads", { exact: false })).toBeNull();
    expect(asFragment()).toMatchSnapshot();
  });

  it('will reload data if "reload" button is clicked', async () => {
    const fetchGamesSpy = jest.fn((_, data) => data);
    apiMocks.setResponseModifier('/api/games', fetchGamesSpy);
    const { getByText } = renderWithProviders(<PastGamesPage />);
    await screen.findAllByText("Rock & Power Ballads", { exact: false });
    expect(fetchGamesSpy).toHaveBeenCalledTimes(1);
    fireEvent.click(getByText('Reload'));
    await waitForExpect(() => {
      expect(fetchGamesSpy).toHaveBeenCalledTimes(2);
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

    renderWithProviders(<PastGamesPage />, { preloadedState });
    await expect(screen.findByText(
      'log out from this guest account and register an account',
      { exact: false })).resolves.toBeDefined();
  });
});