import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../../tests';
import { PopularityGraph } from './PopularityGraph';

import { past } from '../../../tests/fixtures/games.json';

describe('PopularityGraph component', () => {
  const calculateGamesPopularity = (games, vertical) => {
    const themes = {};
    let maxCount = 1;
    games.forEach(game => {
      const key = game.title.replace(/\W/g, '').toLowerCase();
      if (themes[key] === undefined) {
        themes[key] = {
          title: game.title,
          count: 1,
        };
      } else {
        themes[key].count++;
      }
      maxCount = Math.max(maxCount, themes[key].count);
    });
    const keys = Object.keys(themes);
    if (vertical) {
      keys.sort((a, b) => {
        if (a < b) {
          return 1;
        }
        if (b > a) {
          return -1;
        }
        return 0;
      });
    } else {
      keys.sort();
    }
    return keys.map(key => ({
      ...themes[key],
      maxCount,
    }));
  };

  it('to render vertical graph', async () => {
    const popularity = calculateGamesPopularity(past, true);
    const props = {
      popularity,
      toggleOrientation: vi.fn(),
      options: {
        vertical: true
      }
    };
    const result = renderWithProviders(<PopularityGraph {...props} />);
    popularity.forEach((theme) => {
      result.getByText(theme.title);
    });
    fireEvent.click(result.getByRole('button'));
    expect(props.toggleOrientation).toHaveBeenCalledTimes(1);
  });

  it('to render horizontal graph', async () => {
    const popularity = calculateGamesPopularity(past, false);
    const props = {
      popularity,
      toggleOrientation: vi.fn(),
      options: {
        vertical: false
      }
    };
    const result = renderWithProviders(<PopularityGraph {...props} />);
    popularity.forEach((theme) => {
      result.getByText(theme.title);
    });
    fireEvent.click(result.getByRole('button'));
    expect(props.toggleOrientation).toHaveBeenCalledTimes(1);
  });
});