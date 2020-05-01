import { createSlice } from '@reduxjs/toolkit';

import { getCardURL, setCardCheckedURL } from '../endpoints';
import { userIsLoggedIn } from '../user/userSlice';

export function cardInitialState() {
  return ({
    rows: [],
    isFetching: false,
    invalid: true,
    error: null,
    lastUpdated: null,
  });
}
//                    status: cardstatus.enumValueOf(ticket.status),

function cardKey(gamePk, ticketPk) {
  return `${gamePk}_${ticketPk}`;
}

export const cardsSlice = createSlice({
  name: 'cards',
  initialState: {
    cards: {},
    user: -1,
  },
  reducers: {
    requestcard: (state, action) => {
      const { gamePk, ticketPk } = action.payload;
      const key = cardKey(gamePk, ticketPk);
      if (state.cards[key] === undefined) {
        state.cards[key] = cardInitialState();
      }
      state.cards[key].isFetching = true;
    },
    receiveCard: (state, action) => {
      const { timestamp, gamePk, ticketPk, userPk, card } = action.payload;
      const key = cardKey(gamePk, ticketPk);
      state.cards[key] = {
        ...cardInitialState(),
        rows: card.rows,
        invalid: false,
        isFetching: false,
        lastUpdated: timestamp,
      };
      //TODO: use a middleware to clean out cards when user logs in
      state.user = userPk;
    },
    failedFetchCard: (state, action) => {
      const { timestamp, gamePk, ticketPk, error } = action.payload;
      const key = cardKey(gamePk, ticketPk);
      const card = state.cards[key];
      if (!card) {
        return;
      }
      card.isFetching = false;
      card.error = error;
      card.lastUpdated = timestamp;
      card.invalid = true;
      card.rows = [];
    },
    setChecked: (state, action) => {
      const { gamePk, ticketPk, row, column, checked } = action.payload;
      const key = cardKey(gamePk, ticketPk);
      const card = state.cards[key];
      if (!card) {
        return;
      }
      if (row < card.rows.length) {
        const cardRow = card.rows[row];
        if (column < cardRow.length) {
          cardRow[column].checked = checked;
        }
      }
    },
    toggleCell: (state, action) => {
      const { game, cell, ticket } = action.payload;
      const key = cardKey(game.pk, ticket.pk);
      const card = state.cards[key];
      if (!card) {
        return;
      }
      if (cell.row >= card.rows.length) {
        return;
      }
      const row = card.rows[cell.row];
      if (cell.column < row.length) {
        row[cell.column].selected = !row[cell.column].selected;
      }
    }
  },
});

function fetchCard(userPk, gamePk, ticketPk) {
  return dispatch => {
    dispatch(cardsSlice.actions.requestcard({ gamePk, ticketPk }));
    return fetch(getCardURL(gamePk, ticketPk), {
      cache: "no-cache",
      credentials: 'same-origin',
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        return Promise.reject({ error: `${response.status}: ${response.statusText}` });
      })
      .then((result) => {
        const { error } = result;
        if (error === undefined) {
          return dispatch(cardsSlice.actions.receiveCard({ card: result, ticketPk, gamePk, userPk, timestamp: Date.now() }));
        }
        return dispatch(cardsSlice.actions.failedFetchcard({ gamePk, ticketPk, error, timestamp: Date.now() }));
      });
  };
}

function shouldFetchCard(state, gamePk, ticketPk) {
  const { cards, user } = state;
  const key = cardKey(gamePk, ticketPk);
  const card = cards.cards[key];
  if (!card) {
    return true;
  }
  if (user.pk !== cards.user) {
    return true;
  }
  if (card.isFetching) {
    return false;
  }
  return card.invalid;
}

export function fetchCardIfNeeded(gamePk, ticketPk) {
  return (dispatch, getState) => {
    const state = getState();
    if (shouldFetchCard(state, gamePk, ticketPk)) {
      return dispatch(fetchCard(state.user.pk, gamePk, ticketPk));
    }
    const card = state.cards.cards[cardKey(gamePk, ticketPk)];
    return Promise.resolve(card);
  };
}

export function setChecked({ gamePk, ticketPk, row, column, checked }) {
  return (dispatch, getState) => {
    const state = getState();
    const { user } = state;
    if (!userIsLoggedIn(state)) {
      return Promise.reject('Not logged in');
    }
    const number = row * user.options.columns + column;
    dispatch(cardsSlice.actions.setChecked({ gamePk, ticketPk, row, column, checked }));
    return fetch(setCardCheckedURL(gamePk, ticketPk, number), {
      method: (checked ? 'PUT' : 'DELETE'),
      cache: "no-cache",
      credentials: 'same-origin',
    });
  };
}

export const initialState = cardsSlice.initialState;

export const getCard = (state, gamePk, ticketPk) => {
  const key = cardKey(gamePk, ticketPk);
  return state.cards.cards[key];
};

export default cardsSlice.reducer;
