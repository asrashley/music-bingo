import React from 'react';
import { getByText, screen } from '@testing-library/react';
import log from 'loglevel';
import fetchMock from "fetch-mock-jest";

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

import { renderWithProviders, installFetchMocks } from '../../testHelpers';
import { formatDuration } from '../../components/DateTime';
import { TrackListingPage, TrackListingPageComponent } from './TrackListingPage';
import gameFixture from '../../fixtures/game/159.json';
import user from '../../fixtures/userState.json';

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

  it('to render track listing for game 18-04-22-2', async () => {
    const history = {
      push: jest.fn()
    };
    const location = {
      params: {
        gameId: "18-04-22-2"
      }
    };
    const { asFragment, store } = renderWithProviders(<TrackListingPage history={history} match={location} />);
    await screen.findByText(`Track listing for Game ${location.params.gameId}`, { exact: false });
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

  it('fetches game details', async () => {
    const store = createStore({
      ...initialState,
      user,
      games: {
        ...initialState.games,
        games: {
          [gameFixture.pk]: {
            ...gameFixture,
            tracks: [],
            ticketOrder: [],
            isFetchingDetail: false,
            invalidDetail: true,
            invalid: false,
          }
        },
        gameIds: {
          [gameFixture.id]: gameFixture.pk,
        },
        pastOrder: [
          gameFixture.pk
        ],
        user: user.pk,
      }
    });
    const history = {
      push: jest.fn()
    };
    const props = {
      dispatch: store.dispatch,
      game: gameFixture,
      user,
      history
    };
    const fetchGameSpy = jest.fn((_, data) => data);
    apiMocks.setResponseModifier('/api/game/159', fetchGameSpy);
    renderWithProviders(<TrackListingPageComponent {...props} />, { store });
    await screen.findByText(`Track listing for Game ${props.game.id}`, { exact: false });
    expect(fetchGameSpy).toHaveBeenCalledTimes(1);
  });
});