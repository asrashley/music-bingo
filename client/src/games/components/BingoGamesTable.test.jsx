import React from 'react';
import { fireEvent, getByText } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { DateTime } from '../../components/DateTime';
import { BingoGamesTable } from './BingoGamesTable';

describe('BingoGamesTable component', () => {
  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(1670123520000);
  });

  afterAll(() => jest.useRealTimers());

  it('jest setup is using UTC timezone', () => {
    expect(new Date().getTimezoneOffset()).toBe(0);
  });

  it('to render a table of all past games', async () => {
    const userData = await import('../../fixtures/user.json');
    const gamesData = await import('../../fixtures/games.json');
    userData["default"].groups = { "users": true };
    let reloaded = false;
    const onReload = () => reloaded = true;
    const footer = <tr><td>this is the footer</td></tr>;
    gamesData['default'].past.forEach((game, idx) => game.round = (idx + 1));
    const result = renderWithProviders(
      <BingoGamesTable
        title="test of past games"
        games={gamesData['default'].past}
        user={userData['default']}
        onReload={onReload}
        past={true}
        footer={footer}
      />);
    result.getByText("test of past games");
    result.getByText("this is the footer");
    gamesData['default'].past.forEach(game => {
      const tid = `pastgame[${game.pk}]`;
      const row = result.getByTestId(tid);
      getByText(row, DateTime({ date: game.start, ampm: true }));
      expect(row.querySelector(`a[href="/history/game/${game.id}"]`)).not.toBeNull();
    });
    fireEvent.click(result.getByRole('button', { name: "Reload" }));
    expect(reloaded).toBe(true);
    expect(result.asFragment()).toMatchSnapshot();
  });
});
