import React from 'react';
import PropTypes from 'prop-types';
import { saveAs } from 'file-saver';

import { api } from '../../endpoints';
import { BingoCell } from './BingoCell';

import { CellPropType } from '../types/Cell';
import { GameOptionsPropType } from '../../games/types/GameOptions';
import { GamePropType } from '../../games/types/Game';
import { TicketPropType } from '../types/Ticket';

function TableRow({ row, onClick, options }) {
  return (
    <tr>
      {row.map((cell, idx) => <BingoCell key={idx} cell={cell} options={options} onClick={onClick} />)}
    </tr>
  );
}
TableRow.propTypes = {
  row: PropTypes.arrayOf(CellPropType).isRequired,
  onClick: PropTypes.func.isRequired,
  options: GameOptionsPropType.isRequired
};

function CardError({ error }) {
  return (
    <div className="card-error">{error}</div>
  );
}
CardError.propTypes = {
  error: PropTypes.string
};

export class BingoTicket extends React.Component {
  static propTypes = {
    className: PropTypes.string,
    dispatch: PropTypes.func,
    download: PropTypes.bool,
    game: GamePropType.isRequired,
    setChecked: PropTypes.func.isRequired,
    ticket: TicketPropType.isRequired,
  };

  static debounceTime = 250;

  state = {
    error: null,
    debounce: {},
  };

  onClickCell = (touch, cell) => {
    const { game, ticket, setChecked } = this.props;
    const { debounce } = this.state;
    const { row, column } = cell;
    const number = row * game.options.columns + column;
    const clickTimeout = debounce[number];
    const nextDebounce = {
      ...debounce,
      [number]: Date.now() + BingoTicket.debounceTime,
    };

    if (clickTimeout !== undefined && clickTimeout >= Date.now()) {
      this.setState({ debounce: nextDebounce });
      return;
    }
    this.setState(
      () => ({ debounce: nextDebounce }),
      () => setChecked({
        gamePk: game.pk,
        ticketPk: ticket.pk,
        row,
        column,
        number,
        checked: !cell.checked
      }));
  };

  downloadPDF = () => {
    const { game, dispatch, ticket } = this.props;
    return dispatch(api.downloadCard({ gamePk: game.pk, ticketPk: ticket.pk }))
      .then((response) => {
        const filename = `Game ${game.id} - Ticket ${ticket.number}.pdf`;
        return response.payload.blob().then(blob => {
          saveAs(blob, filename);
          return filename;
        });
      });
  };


  render() {
    const { className, game, ticket, download } = this.props;

    return (
      <div className={className || "view-ticket"}>
        {download === true && <div className="download">
          <button className="btn btn-primary btn-lg" onClick={this.downloadPDF}
            disabled={ticket.pk < 1}>
            Download ticket {ticket.number}</button>
        </div>}
        {ticket.error && <CardError error={ticket.error} />}
        <table className="bingo-ticket table"
          data-game-id={game.id} data-ticket-number={ticket.number}>
          <thead>
            <tr>
              <th colSpan={game.options.columns} className="logo">
              </th>
            </tr>
          </thead>
          <tbody>
            {ticket.rows.map((row, idx) => <TableRow key={idx} row={row} options={game.options} onClick={this.onClickCell} />)}
          </tbody>
          <tfoot>
            <tr>
              <th colSpan={game.options.columns - 2} className="footer-title">
                {game.title}
              </th>
              <th colSpan="2" className="footer-number">
                Game {game.id} / Ticket {ticket.number}
              </th>
            </tr>
          </tfoot>
        </table>
      </div>
    );
  }
}
