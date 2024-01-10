import React from 'react';
import { fireEvent, getByText } from '@testing-library/react';

import { renderWithProviders } from '../../../tests';
import { DateTime } from '../../components/DateTime';
import { BingoGamesTable } from './BingoGamesTable';

import { createGameSlug } from '../gamesSlice';

import userData from '../../../tests/fixtures/user.json';
import gamesData from '../../../tests/fixtures/games.json';

describe('BingoGamesTable component', () => {
  beforeAll(() => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(1670123520000);
  });

  afterAll(() => vi.useRealTimers());

  it('vi setup is using UTC timezone', () => {
    expect(new Date().getTimezoneOffset()).toBe(0);
  });

  it('to render a table of all past games', async () => {
    const user = {
      ...userData,
      groups: { "users": true }
    };
    let reloaded = false;
    const onReload = () => reloaded = true;
    const footer = <tr><td>this is the footer</td></tr>;
    const games = {
      games: [],
      past: gamesData.past.map((game, idx) => ({
        ...game,
        slug: createGameSlug(game.title),
        firstGameOfTheDay: idx === 0,
        round: idx + 1,
      })),
    };
    const result = renderWithProviders(
      <BingoGamesTable
        title="test of past games"
        games={games.past}
        user={user}
        onReload={onReload}
        past={true}
        footer={footer}
      />);
    result.getByText("test of past games");
    result.getByText("this is the footer");
    games.past.forEach(game => {
      const tid = `pastgame[${game.pk}]`;
      const row = result.getByTestId(tid);
      getByText(row, DateTime({ date: game.start, ampm: true }));
      expect(row.querySelector(`a[href="/history/games/${game.id}"]`)).not.toBeNull();
    });
    fireEvent.click(result.getByRole('button', { name: "Reload" }));
    expect(reloaded).toBe(true);
    expect(result.asFragment()).toMatchSnapshot();
  });
});
