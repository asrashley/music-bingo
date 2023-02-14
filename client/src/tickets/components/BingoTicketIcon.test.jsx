import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { DateTime } from '../../components/DateTime';
import { BingoTicketIcon } from './BingoTicketIcon';

import * as user from '../../fixtures/userState.json';

describe('BingoTicketIcon component', () => {
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

  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(1670123520000);
  });

  afterAll(() => jest.useRealTimers());

  it('renders a ticket that is available', () => {
    const props = {
      game,
      user,
      usersMap: {},
      onClick: jest.fn(),
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
    const result = renderWithProviders(<BingoTicketIcon {...props} />);
    const btn = result.getByRole('button');
    expect(btn).toHaveClass('bingo-ticket');
    expect(btn).toHaveClass('available');
    expect(btn).toHaveClass(props.game.options.colour_scheme);
    expect(btn).not.toHaveClass('mine');
    expect(btn).not.toHaveClass('taken');
    fireEvent.click(btn);
    expect(props.onClick).toHaveBeenCalledTimes(1);
  });

  it('renders a ticket that is mine', () => {
    const props = {
      game,
      user,
      usersMap: {},
      onClick: jest.fn(),
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
      onClick: jest.fn(),
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
