import React from 'react';

import { renderWithProviders } from '../../../tests';
import { BingoTicketIcon } from './BingoTicketIcon';

import user from '../../../tests/fixtures/userState.json';

describe('BingoTicketIcon component', () => {
  const game = {
    "pk": 159,
    "id": "18-04-22-2",
    "title": "Various Artists",
    "slug": "various-artists",
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

  /*beforeAll(() => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(1670123520000);
  });*/

  afterAll(() => vi.useRealTimers());

  it('renders a ticket that is available', async () => {
    const props = {
      game,
      user: {
        ...user,
        groups: {
          users: true,
        },
      },
      usersMap: {},
      maxTickets: 2,
      selected: 0
    };
    props.ticket = {
      pk: 1,
      number: 1,
      game: props.game.pk,
      title: '',
      tracks: [],
      checked: 0,
      user: null,
      lastUpdated: null,
    };
    const { events, getByRole, findByText } = renderWithProviders(<BingoTicketIcon {...props} />);
    const btn = getByRole('button');
    expect(btn).toHaveClass('bingo-ticket');
    expect(btn).toHaveClass('available');
    expect(btn).toHaveClass(props.game.options.colour_scheme);
    expect(btn).not.toHaveClass('mine');
    expect(btn).not.toHaveClass('taken');
    await events.click(btn);
    //expect(props.onClick).toHaveBeenCalledTimes(1);
    await findByText('Confirm ticket choice');
  });


  it('shows admin menu', async () => {
    const props = {
      game,
      user,
      usersMap: {},
      maxTickets: 2,
      selected: 0
    };
    props.ticket = {
      pk: 1,
      number: 1,
      game: props.game.pk,
      title: '',
      tracks: [],
      checked: 0,
      user: null,
      lastUpdated: null,
    };
    const { events, getByRole, findByText } = renderWithProviders(<BingoTicketIcon {...props} />);
    const btn = getByRole('button');
    expect(btn).toHaveClass('bingo-ticket');
    expect(btn).toHaveClass('available');
    expect(btn).toHaveClass(props.game.options.colour_scheme);
    expect(btn).not.toHaveClass('mine');
    expect(btn).not.toHaveClass('taken');
    await events.click(btn);
    await findByText('View Ticket');
    await findByText('Claim Ticket');
  });

  it('renders a ticket that is mine', () => {
    const props = {
      game,
      user,
      usersMap: {},
      maxTickets: 2,
      selected: 0
    };
    props.ticket = {
      pk: 1,
      number: 1,
      game: props.game.pk,
      title: '',
      tracks: [],
      checked: 0,
      user: props.user.pk,
      lastUpdated: null,
    };
    const result = renderWithProviders(<BingoTicketIcon {...props} />);
    const btn = result.getByRole('button');
    expect(btn).not.toHaveClass('available');
    expect(btn).toHaveClass('mine');
  });

  it('renders a ticket that is taken by another user', () => {
    const props = {
      game,
      user,
      usersMap: {},
      maxTickets: 2,
      selected: 0
    };
    props.ticket = {
      pk: 1,
      number: 1,
      game: props.game.pk,
      title: '',
      tracks: [],
      checked: 0,
      user: props.user.pk + 2,
      lastUpdated: null,
    };
    const result = renderWithProviders(<BingoTicketIcon {...props} />);
    const btn = result.getByRole('button');
    expect(btn).toHaveClass('taken');
    expect(btn).not.toHaveClass('available');
    expect(btn).not.toHaveClass('mine');
  });
});
