import React from 'react';
import { fireEvent, getByText } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { TrackListingPage, TrackListingPageComponent } from './TrackListingPage';
import gameFixture from '../../fixtures/game/159.json';
import user from '../../fixtures/userState.json';

const game = {
  ...gameFixture,
  slug: 'slug',
};

describe('TrackListingPage component', () => {
  let apiMocks;

  beforeEach(() => {
    apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
  });

  afterEach(() => {
    fetchMock.mockReset();
    log.resetLevel();
    apiMocks = null;
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('to render track listing for game 18-04-22-2', async () => {
    const preloadedState = {
      ...initialState,
      routes: {
        params: {
          gameId: "18-04-22-2"
        }
      }
    };
    const { findByText, findByTestId, store } = renderWithProviders(<TrackListingPage />, {
      preloadedState
    });
    await findByText(`Track listing for Game 18-04-22-2`, { exact: false });
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
  });

  it('fetches game details on mounting component', async () => {
    const store = createStore({
      ...initialState,
      user,
      games: {
        ...initialState.games,
        games: {
          [game.pk]: {
            ...game,
            tracks: [],
            ticketOrder: [],
            isFetchingDetail: false,
            invalidDetail: true,
            invalid: false,
          }
        },
        gameIds: {
          [game.id]: game.pk,
        },
        pastOrder: [
          game.pk
        ],
        user: user.pk,
      },
      routes: {
        params: {
          gameId: game.id,
        },
      },
    });
    const props = {
      dispatch: store.dispatch,
      game,
      user,
    };
    const fetchGameSpy = vi.fn((_, data) => data);
    apiMocks.setResponseModifier('/api/game/159', fetchGameSpy);
    const { findByText } = renderWithProviders(<TrackListingPageComponent {...props} />, { store });
    await findByText(`Track listing for Game ${props.game.id}`, { exact: false });
    await findByText("Dancing In The Moonlight");
    expect(fetchGameSpy).toHaveBeenCalledTimes(1);
  });

  it('reloads game details when refresh is clicked', async () => {
    const store = createStore({
      ...initialState,
      user,
      games: {
        ...initialState.games,
        games: {
          [game.pk]: {
            ...game,
            isFetchingDetail: false,
            invalidDetail: false,
            invalid: false,
          }
        },
        gameIds: {
          [game.id]: game.pk,
        },
        pastOrder: [
          game.pk
        ],
        user: user.pk,
      }
    });
    const props = {
      dispatch: store.dispatch,
      game,
      user,
    };
    const fetchGameSpy = vi.fn((_, data) => data);
    apiMocks.setResponseModifier('/api/game/159', fetchGameSpy);
    const { findByText } = renderWithProviders(<TrackListingPageComponent {...props} />, { store });
    await findByText(`Track listing for Game ${props.game.id}`, { exact: false });
    expect(fetchGameSpy).toHaveBeenCalledTimes(0);
    fireEvent.click(document.querySelector('button.refresh-icon'));
    await waitForExpect(() => {
      expect(fetchGameSpy).toHaveBeenCalledTimes(1);
    });
  });
});