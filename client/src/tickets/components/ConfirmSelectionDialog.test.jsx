import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import waitForExpect from 'wait-for-expect';
import log from 'loglevel';

import { renderWithProviders } from '../../testHelpers';
import { ConfirmSelectionDialog } from './ConfirmSelectionDialog';

import game from '../../fixtures/game/159.json';
import ticket from '../../fixtures/ticket.json';
import user from '../../fixtures/userState.json';

describe('ConfirmSelectionDialog component', () => {
  const users = {};
  beforeAll(() => {
    for (let i = 0; i < 5; ++i) {
      const usr = {
        username: `user${i + 1}`,
        email: `user${i + 1}@music.bingo`,
        pk: i + 2,
        groups: {
          "users": true,
        }
      };
      users[usr.pk] = usr;
    }
  });

  afterEach(log.resetLevel);

  it('shows dialog to select a ticket', async () => {
    const props = {
      ticket: {
        ...ticket,
        user: 0
      },
      user,
      onCancel: jest.fn(),
      onConfirm: jest.fn(),
    };
    const result = renderWithProviders(
      <ConfirmSelectionDialog {...props} />);
    result.getByText(`Would you like to choose ticket ${props.ticket.number}?`, { exact: false });
    fireEvent.click(result.getByText('Cancel'));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
    fireEvent.click(result.getByText('Yes Please'));
    expect(props.onConfirm).toHaveBeenCalledTimes(1);
  });

  it('shows dialog to release ticket owned by user', async () => {
    const props = {
      ticket: {
        ...ticket,
        user: user.pk
      },
      user,
      onCancel: jest.fn(),
      onConfirm: jest.fn(),
    };
    const result = renderWithProviders(
      <ConfirmSelectionDialog {...props} />);
    result.getByText(`Would you like to release ticket ${props.ticket.number}?`, { exact: false });
    result.getByText('This ticket is owned by you');
    fireEvent.click(result.getByText('Cancel'));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
    fireEvent.click(result.getByText('Yes Please'));
    expect(props.onConfirm).toHaveBeenCalledTimes(1);
  });

  it('shows dialog to release ticket owned by someone else', async () => {
    const props = {
      ticket: {
        ...ticket,
        user: 3
      },
      user: {
        ...user,
        users
      },
      onCancel: jest.fn(),
      onConfirm: jest.fn(),
    };
    const result = renderWithProviders(
      <ConfirmSelectionDialog {...props} />);
    result.getByText(`Would you like to release ticket ${props.ticket.number}?`, { exact: false });
    result.getByText(`This ticket is owned by ${users[3].username}`);
    fireEvent.click(result.getByText('Cancel'));
    expect(props.onCancel).toHaveBeenCalledTimes(1);
    fireEvent.click(result.getByText('Yes Please'));
    expect(props.onConfirm).toHaveBeenCalledTimes(1);
  });

});
