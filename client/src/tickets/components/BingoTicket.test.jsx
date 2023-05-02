import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';
import { BingoTicket } from './BingoTicket';

describe('BingoTicket component', () => {
  const game = {
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
  };

  it('renders a ticket that is available', async () => {
    const ticketData = await import('../../fixtures/ticket.json');
    const props = {
      game,
      ticket: ticketData['default'],
      setChecked: jest.fn(),
      download: false,
    };
    props.ticket.game = game.pk;
    const store = createStore(initialState);
    props.dispatch = store.dispatch;
    const result = renderWithProviders(<BingoTicket {...props} />, { store });
    props.ticket.rows.forEach((row) => {
      row.forEach(cell => {
        result.getByText(cell.title);
      });
    });
    const cell = result.getByText(props.ticket.rows[0][0].title);
    fireEvent.click(cell);
    expect(props.setChecked).toHaveBeenCalledTimes(1);

    expect(result.asFragment()).toMatchSnapshot();
  });
});
