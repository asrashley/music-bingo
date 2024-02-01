import React from 'react';
import { fireEvent } from '@testing-library/react';
import log from 'loglevel';

import { renderWithProviders } from '../../../tests';
import { AdminTicketDialog } from './AdminTicketDialog';

import game from '../../../tests/fixtures/game/159.json';
import ticket from '../../../tests/fixtures/ticket.json';
import user from '../../../tests/fixtures/userState.json';

describe('AdminTicketDialog component', () => {
  const users = [];
  beforeAll(() => {
    const options = {
      "colourScheme": "cyan",
      "colourSchemes": [
        "blue",
        "christmas",
        "cyan",
        "green",
        "grey",
        "magenta",
        "orange",
        "pink",
        "pride",
        "purple",
        "red",
        "yellow"
      ],
      "maxTickets": 2,
      "rows": 3,
      "columns": 5
    };
    for (let i = 0; i < 5; ++i) {
      users.push({
        username: `user${i + 1}`,
        email: `user${i + 1}@music.bingo`,
        pk: i + 2,
        groups: {
          "users": true,
        },
        options
      });
    }
  });

  afterEach(log.resetLevel);

  it('shows dialog for an unclaimed ticket', async () => {
    const props = {
      game: {
        ...game,
        slug: 'slug',
      },
      ticket,
      user,
      usersMap: {},
      onCancel: vi.fn(),
      onAdd: vi.fn(),
      onRelease: vi.fn(),
      onView: vi.fn()
    };
    const { events, getAllByText, getByText } = renderWithProviders(
      <AdminTicketDialog {...props} />);
    getAllByText(`Ticket ${props.ticket.number}`);
    await events.click(getByText('Cancel'));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
    await events.click(getByText('Claim Ticket'));
    expect(props.onAdd).toHaveBeenCalledTimes(1);
  });

  it('shows dialog for a ticket claimed by another user', async () => {
    const usersMap = {
      5: {
        username: 'AnotherUser'
      }
    };
    const props = {
      game: {
        ...game,
        slug: 'slug',
      },
      ticket: {
        ...ticket,
        user: 5
      },
      user,
      usersMap,
      onCancel: vi.fn(),
      onAdd: vi.fn(),
      onRelease: vi.fn(),
      onView: vi.fn()
    };
    const result = renderWithProviders(
      <AdminTicketDialog {...props} />);
    result.getAllByText(`Ticket ${props.ticket.number}`);
    result.getByText('This ticket is owned by AnotherUser');
    fireEvent.click(result.getByText('Release Ticket'));
    expect(props.onRelease).toHaveBeenCalledTimes(1);
  });
});
