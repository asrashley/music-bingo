import React from 'react';
import { getByText } from '@testing-library/react';
import log from 'loglevel';
import waitForExpect from 'wait-for-expect';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { fetchMock, renderWithProviders, installFetchMocks } from '../../../tests';
import { formatDuration } from '../../components/DateTime';
import { TrackListingPage, TrackListingPageComponent } from './TrackListingPage';
import gameFixture from '../../../tests/fixtures/game/159.json';
import { adminUser, normalUser } from '../../../tests/MockServer';

const game = {
  ...gameFixture,
  slug: 'slug',
};

describe('TrackListingPage component', () => {
  let mockServer, user;
  beforeEach(() => {
    mockServer = installFetchMocks(fetchMock, { loggedIn: true });
    user = mockServer.getUserState(normalUser);
  });

  afterEach(() => {
    mockServer.shutdown();
    fetchMock.mockReset();
    log.resetLevel();
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  it('to render track listing for game 18-04-22-2', async () => {

    const preloadedState = {
      ...initialState,
      user,
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
    const { findByText } = renderWithProviders(<TrackListingPageComponent {...props} />, { store });
    await findByText(`Track listing for Game ${props.game.id}`, { exact: false });
    await findByText("Dancing In The Moonlight");
    expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(1);
  });

  it('reloads game details when refresh is clicked', async () => {
    const admin = mockServer.getUserState(adminUser);
    const store = createStore({
      ...initialState,
      user: admin,
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
        user: admin.pk,
      }
    });
    const props = {
      dispatch: store.dispatch,
      game,
      user: admin,
    };
    const { events, findByText, findBySelector } = renderWithProviders(<TrackListingPageComponent {...props} />, { store });
    await findByText(`Track listing for Game ${props.game.id}`, { exact: false });
    expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(0);
    await events.click(await findBySelector('button.refresh-icon'));
    await waitForExpect(() => {
      expect(fetchMock.calls('/api/game/159', 'GET').length).toEqual(1);
    });
  });
});