import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { BingoCell } from './BingoCell';

function CellWrapper(props) {
  return (
    <table>
      <tbody>
        <tr>
          <BingoCell {...props} />
        </tr>
      </tbody>
    </table>
  );
}

describe('BingoCell component', () => {
  const options = {
    colour_scheme: 'blue',
    columns: 5,
    rows: 3,
    include_artist: true,
    number_of_cards: 20
  };
  const cell = {
    title: 'song title',
    artist: 'song artist',
    background: '',
    checked: false
  };

  it('renders both title and artist when include_artist is true', () => {
    const props = {
      cell,
      onClick: jest.fn(),
      options
    };
    const result = renderWithProviders(<CellWrapper {...props} />);
    result.getByText(cell.title);
    result.getByText(cell.artist);
    const tdCell = result.container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).not.toHaveClass('ticked');
    fireEvent.click(tdCell);
    expect(props.onClick).toHaveBeenCalledTimes(1);
    expect(props.onClick.mock.calls[0]).toEqual(['click', cell]);
  });

  it('responds to touch events', () => {
    const props = {
      cell,
      onClick: jest.fn(),
      options
    };
    const { container } = renderWithProviders(<CellWrapper {...props} />);
    const tdCell = container.querySelector('td');
    fireEvent.touchStart(tdCell);
    expect(props.onClick).toHaveBeenCalledTimes(1);
    expect(props.onClick.mock.calls[0]).toEqual(['touch', cell]);
  });

  it('ticks cell if it has been selected', () => {
    const props = {
      cell: {
        ...cell,
        checked: true,
      },
      onClick: jest.fn(),
      options
    };
    const result = renderWithProviders(<CellWrapper {...props} />);
    result.getByText(cell.title);
    result.getByText(cell.artist);
    const tdCell = result.container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).toHaveClass('ticked');
  });

  it('renders only title when include_artist is false', () => {
    const props = {
      cell,
      onClick: jest.fn(),
      options: {
        ...options,
        include_artist: false
      }
    };
    const result = renderWithProviders(<CellWrapper {...props} />);
    result.getByText(cell.title);
    expect(result.queryByText(cell.artist)).toBeNull();
    const tdCell = result.container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).not.toHaveClass('ticked');
  });
});
