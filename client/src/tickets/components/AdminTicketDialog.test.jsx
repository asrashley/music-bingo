import React from 'react';
import { fireEvent } from '@testing-library/react';
import log from 'loglevel';

import { renderWithProviders } from '../../testHelpers';
import { AdminTicketDialog } from './AdminTicketDialog';

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
    const [gameData, ticketData, userData] = await Promise.all([
      import('../../fixtures/game/159.json'),
      import('../../fixtures/ticket.json'),
      import('../../fixtures/userState.json')
    ]);
    const props = {
      game: gameData.default,
      ticket: ticketData.default,
      user: userData.default,
      usersMap: {},
      onCancel: jest.fn(),
      onAdd: jest.fn(),
      onRelease: jest.fn()
    };
    const result = renderWithProviders(
      <AdminTicketDialog {...props} />);
    result.getAllByText(`Ticket ${props.ticket.number}`);
    fireEvent.click(result.getByText('Cancel'));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
    fireEvent.click(result.getByText('Claim Ticket'));
    expect(props.onAdd).toHaveBeenCalledTimes(1);
  });

  it('shows dialog for a ticket claimed by another user', async () => {
    const [gameData, ticketData, userData] = await Promise.all([
      import('../../fixtures/game/159.json'),
      import('../../fixtures/ticket.json'),
      import('../../fixtures/userState.json')
    ]);
    const usersMap = {
      5: {
        username: 'AnotherUser'
      }
    };
    const props = {
      game: gameData.default,
      ticket: {
        ...ticketData.default,
        user: 5
      },
      user: userData.default,
      usersMap,
      onCancel: jest.fn(),
      onAdd: jest.fn(),
      onRelease: jest.fn()
    };
    const result = renderWithProviders(
      <AdminTicketDialog {...props} />);
    result.getAllByText(`Ticket ${props.ticket.number}`);
    result.getByText('This ticket is owned by AnotherUser');
    fireEvent.click(result.getByText('Release Ticket'));
    expect(props.onRelease).toHaveBeenCalledTimes(1);
  });
});
