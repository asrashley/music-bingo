import log from 'loglevel';

import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { gamesSlice } from './gamesSlice';

function createInitialStore() {
  const games = {
    '2': {
      "pk": 2,
      "id": "18-04-25-2",
      "title": "Pot Luck",
      "start": "2018-04-05T20:43:00Z",
      "end": "2018-04-06T19:43:40Z",
      "options": {
        "colour_scheme": "green",
        "number_of_cards": 24,
        "include_artist": true,
        "page_size": "A4",
        "columns": 5,
        "rows": 3,
        "checkbox": false,
        "cards_per_page": 4,
        "backgrounds": ["#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9", "#f0fff0", "#d9ffd9"]
      },
      "userCount": 0
    },
    '1': {
      "pk": 1,
      "id": "18-04-25-1",
      "title": "Rock",
      "start": "2018-04-06T19:24:25Z",
      "end": "2018-04-06T19:24:25Z",
      "options": {
        "colour_scheme": "blue",
        "number_of_cards": 24,
        "include_artist": true,
        "page_size": "A4",
        "columns": 5,
        "rows": 3,
        "checkbox": false,
        "cards_per_page": 4,
        "backgrounds": ["#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff"]
      },
      "userCount": 0
    },
    '159': {
      "pk": 159,
      "id": "18-04-22-2",
      "title": "Various Artists",
      "start": "2018-04-22T15:43:56Z",
      "end": "2018-04-23T15:43:56Z",
      "options": {
        "colour_scheme": "blue",
        "number_of_cards": 36,
        "include_artist": true,
        "page_size": "A4",
        "columns": 5,
        "rows": 3,
        "checkbox": false,
        "cards_per_page": 4,
        "backgrounds": ["#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff", "#f0f8ff", "#daedff"]
      },
      "userCount": 0
    }
  };
  const isPast = new Date().toISOString() > games[159].start;
  const pastOrder = isPast ? [2, 1, 159] : [];
  const order = isPast ? [] : [2, 1, 159];
  const gameIds = {};
  Object.values(games).forEach((game) => gameIds[game.id] = game.pk);
  const store = createStore({
    ...initialState,
    games: {
      ...initialState.games,
      games,
      gameIds,
      order,
      pastOrder,
      invalid: false,
      error: null
    }
  }, false);
  return ({
    store, games, order, pastOrder, gameIds
  });
}

describe('gamesSlice', () => {
  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('04 Dec 2022 03:12:00 GMT').getTime());
  });

  afterAll(() => jest.useRealTimers());

  afterEach(() => log.resetLevel());

  it('invalidates state', async () => {
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        games: {
          123: { id: '2023-03-02' }
        },
        order: [123],
        invalid: false,
      }
    }, false);
    expect(store.getState().games.invalid).toEqual(false);
    await store.dispatch(gamesSlice.actions.invalidateGames());
    expect(store.getState().games.invalid).toEqual(true);
    expect(store.getState().games.games).toEqual({});
  });

  it('records if fetching games failed', () => {
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        invalid: false,
        error: null
      }
    }, false);
    store.dispatch(gamesSlice.actions.failedFetchGames({
      timestamp: 1234,
      error: 'an error message'
    }));
    const { invalid, error, lastUpdated } = store.getState().games;
    expect(invalid).toEqual(true);
    expect(error).toEqual('an error message');
    expect(lastUpdated).toEqual(1234);
  });

  it('records if modifying a game fails', () => {
    const game = {
      pk: 123,
      id: '2023-02-01',
      isModifying: true
    };
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        games: {
          [game.pk]: game
        },
        gameIds: {
          [game.id]: game.pk
        },
        order: [game.pk],
        invalid: false,
        error: null
      }
    }, false);
    store.dispatch(gamesSlice.actions.failedModifyGame({
      gamePk: game.pk
    }));
    const { games } = store.getState().games;
    expect(games[game.pk].isModifying).toEqual(false);
  });

  it('records if importing a game fails', () => {
    const store = createStore({
      ...initialState,
      games: {
        ...initialState.games,
        invalid: false,
        error: null
      }
    }, false);
    store.dispatch(gamesSlice.actions.importGameFailed({
      timestamp: 1234,
      error: 'an error message'
    }));
    const { done, errors, timestamp } = store.getState().games.importing;
    expect(done).toEqual(true);
    expect(errors).toEqual(['an error message']);
    expect(timestamp).toEqual(1234);
  });

  it('updates order of past games when a game start or end time is modified', () => {
    jest.setSystemTime(new Date('04 Dec 2022 03:12:00 GMT').getTime());
    const { store, games } = createInitialStore();
    expect(store.getState().games.order).toEqual([]);
    expect(store.getState().games.pastOrder).toEqual([2, 1, 159]);
    store.dispatch(gamesSlice.actions.receiveGameModification({
      timestamp: Date.now(),
      payload: {
        game: {
          ...games[2],
          title: 'new game title',
          start: "2018-04-12T15:43:56Z",
          end: "2018-04-13T15:43:56Z",
        }
      },
      gamePk: 2
    }));
    const curState = store.getState();
    expect(curState.games.order).toEqual([]);
    expect(curState.games.pastOrder).toEqual([1, 2, 159]);
  });

  it('updates order of active games when a game start or end time is modified', () => {
    jest.setSystemTime(new Date("2018-04-05T20:43:00Z").getTime());
    const { store, games } = createInitialStore();
    expect(store.getState().games.pastOrder).toEqual([]);
    expect(store.getState().games.order).toEqual([2, 1, 159]);
    store.dispatch(gamesSlice.actions.receiveGameModification({
      timestamp: Date.now(),
      payload: {
        game: {
          ...games[2],
          title: 'new game title',
          start: "2018-04-12T15:43:56Z",
          end: "2018-04-13T15:43:56Z",
        }
      },
      gamePk: 2
    }));
    const curState = store.getState();
    expect(curState.games.pastOrder).toEqual([]);
    expect(curState.games.order).toEqual([1, 2, 159]);
  });
});