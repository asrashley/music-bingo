import { createStore } from '../store/createStore';
import {
  ticketsSlice, initialState, gameInitialState, ticketInitialState, shouldFetchTickets,
} from './ticketsSlice';

describe('ticketsSlice', () => {
  const game = {
    ...gameInitialState(),
    'id': '2023-02-01',
    pk: 123,
    invalid: false
  };
  const ticket = {
    ...ticketInitialState(),
    pk: 234,
    isFetching: false,
    game: game.pk,
    number: 5
  };

  it('to reset state if a new user logs in', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        },
        tickets: {
          [ticket.pk]: ticket
        }
      }
    });
    const user = {
      pk: 2
    };
    store.dispatch(ticketsSlice.actions.receiveUser({ payload: user }));
    const { tickets } = store.getState();
    expect(tickets.user).toEqual(user.pk);
    expect(tickets.games).toEqual({});
    expect(tickets.tickets).toEqual({});
  });

  it('updates games isFetching state when requesting status update', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        }
      }
    });
    expect(store.getState().tickets.games[game.pk].isFetching).toEqual(false);
    store.dispatch(ticketsSlice.actions.requestStatusUpdate({ gamePk: game.pk }));
    const { tickets } = store.getState();
    expect(tickets.games[game.pk].isFetching).toEqual(true);
  });

  it('updates state if fetching game failed', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        }
      }
    });
    expect(store.getState().tickets.games[123].isFetching).toEqual(false);
    store.dispatch(ticketsSlice.actions.failedFetchTickets({
      timestamp: 54321,
      error: 'an error message',
      gamePk: game.pk
    }));
    const { tickets } = store.getState();
    expect(tickets.games[game.pk]).toEqual({
      ...game,
      lastUpdated: 54321,
      invalid: true,
      error: 'an error message'
    });
  });

  it('updates state of ticket when claimed', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        },
        tickets: {
          [ticket.pk]: ticket
        }
      }
    });
    store.dispatch(ticketsSlice.actions.receiveStatusUpdate({
      payload: {
        claimed: {
          [ticket.pk]: 3
        }
      },
      gamePk: game.pk,
      timestamp: 45677
    }));
    const { tickets } = store.getState();
    const g = tickets.games[game.pk];
    expect(g.lastUpdated).toEqual(45677);
    const t = tickets.tickets[ticket.pk];
    expect(t.user).toEqual(3);
    expect(t.lastUpdated).toEqual(45677);
  });

  it('updates state of ticket when released', () => {
    const user = {
      pk: 3,
      email: 'a.user@unit.test',
      username: 'abcdef'
    };
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        },
        tickets: {
          [ticket.pk]: {
            ...ticket,
            user: user.pk
          }
        }
      }
    });
    /* an unknown game should not change the state */
    const before = store.getState();
    store.dispatch(ticketsSlice.actions.confirmRemoveTicket({
      ticketPk: ticket.pk,
      gamePk: game.pk + 1,
      timestamp: 333,
      user
    }));
    expect(store.getState()).toEqual(before);

    store.dispatch(ticketsSlice.actions.confirmRemoveTicket({
      ticketPk: ticket.pk,
      gamePk: game.pk,
      timestamp: 45677,
      user
    }));
    const { tickets } = store.getState();
    const t = tickets.tickets[ticket.pk];
    expect(t.user).toEqual(null);
    expect(t.lastUpdated).toEqual(45677);
  });

  it('updates state if fetching ticket detail failed', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        },
        tickets: {
          [ticket.pk]: ticket
        }
      }
    });
    expect(store.getState().tickets.games[123].isFetching).toEqual(false);
    store.dispatch(ticketsSlice.actions.failedFetchTicketDetail({
      timestamp: 54321,
      ticketPk: ticket.pk,
      error: 'an error message'
    }));
    const { tickets } = store.getState();
    expect(tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      lastUpdated: 54321,
      error: 'an error message'
    });
  });

  it('sets and clears check on songs within a ticket', () => {
    const store = createStore({
      tickets: {
        ...initialState,
        user: 1,
        games: {
          [game.pk]: game
        },
        tickets: {
          [ticket.pk]: ticket
        }
      }
    });

    store.dispatch(ticketsSlice.actions.setChecked({
      number: 3,
      ticketPk: ticket.pk,
      checked: true
    }));
    expect(store.getState().tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      checked: (1 << 3)
    });

    store.dispatch(ticketsSlice.actions.setChecked({
      number: 1,
      ticketPk: ticket.pk,
      checked: true
    }));
    expect(store.getState().tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      checked: (1 << 3) + (1 << 1)
    });

    store.dispatch(ticketsSlice.actions.setChecked({
      number: 1,
      ticketPk: ticket.pk,
      checked: false
    }));
    expect(store.getState().tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      checked: (1 << 3)
    });

    store.dispatch(ticketsSlice.actions.toggleCell({
      number: 4,
      ticketPk: ticket.pk,
      checked: false
    }));
    expect(store.getState().tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      checked: (1 << 3) + (1 << 4)
    });

    store.dispatch(ticketsSlice.actions.toggleCell({
      number: 4,
      ticketPk: ticket.pk,
      checked: false
    }));
    expect(store.getState().tickets.tickets[ticket.pk]).toEqual({
      ...ticket,
      checked: (1 << 3)
    });
  });

  it('should detect when to fetch tickets', () => {
    const user = {
      pk: 12,
      username: "admin",
      email: "admin@music.bingo",
    };
    const state = {
      games: {},
      tickets: {
        user: user.pk
      },
      user
    };
    expect(shouldFetchTickets(state, 33)).toEqual(true);
    state.games[33] = {
      isFetching: false,
      invalid: false,
    };
    expect(shouldFetchTickets(state, 33)).toEqual(false);
    state.games[33] = {
      isFetching: false,
      invalid: true,
    };
    expect(shouldFetchTickets(state, 33)).toEqual(true);
    state.games[33] = {
      isFetching: true,
      invalid: true,
    };
    expect(shouldFetchTickets(state, 33)).toEqual(false);
    state.games[33] = {
      isFetching: false,
      invalid: false,
    };
    state.tickets.user = 4;
    expect(shouldFetchTickets(state, 33)).toEqual(true);
  });
});