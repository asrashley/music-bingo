import { createSelector } from 'reselect';

import { cardKey } from './cardsSlice';

const getOptions = (state, props) => state.user.options;

const getGamePk = (state, props) => {
  if (props.game) {
    return props.game.pk;
  }
  return props.match.params.gamePk;
};

const getTicketPk = (state, props) => {
  if (props.ticket) {
    return props.ticket.pk;
  }
  return props.match.params.ticketPk;
};

const getCards = (state, props) => state.cards.cards;

export const getCard = createSelector(
  [getGamePk, getTicketPk, getCards, getOptions],
  (gamePk, ticketPk, cards, options) => {
    const key = cardKey(gamePk, ticketPk);
    let card = cards[key];
    if (!card || card.isFetching || card.error) {
      const cell = { title: '', artist: '' };
      const row = [];
      for (let i = 0; i < options.columns; ++i) {
        row.push(cell);
      }
      card = {
        rows: [],
        placeholder: true,
        isFetching: card ? card.isFetching : false,
        error: card ? card.error : null,
      };
      for (let i = 0; i < options.rows; ++i) {
        card.rows.push(row);
      }
    }
    return card;
  });

