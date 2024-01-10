import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../../tests';
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

  it('renders both title and artist when include_artist is true', async () => {
    const props = {
      cell,
      onClick: vi.fn(),
      options
    };
    const { events, getByText, container } = renderWithProviders(<CellWrapper {...props} />);
    getByText(cell.title);
    getByText(cell.artist);
    const tdCell = container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).not.toHaveClass('ticked');
    await events.click(tdCell);
    expect(props.onClick).toHaveBeenCalledTimes(1);
    expect(props.onClick.mock.calls[0]).toEqual(['click', cell]);
  });

  it('responds to touch events', async () => {
    const props = {
      cell,
      onClick: vi.fn(),
      options
    };
    const { container } = renderWithProviders(<CellWrapper {...props} />);
    const tdCell = container.querySelector('td');
    fireEvent.touchStart(tdCell);
    /* await events.pointer([
      { keys: '[TouchA>]', target: tdCell },
      { keys: '[/TouchA]' }
    ]); */
    expect(props.onClick).toHaveBeenCalledTimes(1);
    expect(props.onClick.mock.calls[0]).toEqual(['touch', cell]);
  });

  it('ticks cell if it has been selected', () => {
    const props = {
      cell: {
        ...cell,
        checked: true,
      },
      onClick: vi.fn(),
      options
    };
    const { container, getByText } = renderWithProviders(<CellWrapper {...props} />);
    getByText(cell.title);
    getByText(cell.artist);
    const tdCell = container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).toHaveClass('ticked');
  });

  it('renders only title when include_artist is false', () => {
    const props = {
      cell,
      onClick: vi.fn(),
      options: {
        ...options,
        include_artist: false
      }
    };
    const { container, getByText, queryByText } = renderWithProviders(<CellWrapper {...props} />);
    getByText(cell.title);
    expect(queryByText(cell.artist)).toBeNull();
    const tdCell = container.querySelector('td');
    expect(tdCell).toHaveClass('bingo-cell');
    expect(tdCell).not.toHaveClass('ticked');
  });
});
