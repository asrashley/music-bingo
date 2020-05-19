import React from 'react';
import PropTypes from 'prop-types';
import { saveAs } from 'file-saver';

import { api } from '../../endpoints';

const BingoCell = ({ cell, onClick, options }) => {
  const tdStyle = {
    width: `${100 / options.columns}%`,
  };
  if (cell.background) {
    tdStyle.backgroundColor = cell.background;
  }
  let className = "bingo-cell";
  if (cell.checked === true) {
    className += " ticked";
  }
  return (
    <td className={className} onClick={(ev) => onClick(cell)}
      onTouchStart={(ev) => onClick(cell)}
      data-row={cell.row} data-column={cell.column}
      style={tdStyle}
    >
      <div className="bingo-cell-wrap">
        <p className="title">{cell.title}</p>
        <p className="artist">{cell.artist}</p>
      </div>
    </td>
  );
};

const TableRow = ({ row, onClick, options }) => {
  return (
    < tr >
      {row.map((cell, idx) => <BingoCell key={idx} cell={cell} options={options} onClick={onClick} />)}
    </tr>
  );
};

const CardError = ({ error }) => {
  return (
    <div class="card-error">{error}</div>
  );
};

class BingoTicket extends React.Component {
  static propTypes = {
    game: PropTypes.object.isRequired,
    ticket: PropTypes.object.isRequired,
    setChecked: PropTypes.func.isRequired,
    download: PropTypes.bool,
  };

  state = {
    error: null,
  };
  
  onClickCell = (cell) => {
    const { game, ticket, setChecked } = this.props;
    const { row, column } = cell;
    const number = row * game.options.columns + column;

    setChecked({
      gamePk: game.pk,
      ticketPk: ticket.pk,
      row,
      column,
      number,
      checked: !cell.checked
    });
  };

  downloadPDF = (ev) => {
    const { game, dispatch, ticket } = this.props;
    return dispatch(api.downloadCard({ gamePk: game.pk, ticketPk: ticket.pk }))
      .then((response) => {
        const filename = `Game ${game.id} - Ticket ${ticket.number}.pdf`;
        return response.payload.blob().then(blob => {
          saveAs(blob, filename);
          return filename;
        });
      })
      .catch(err => this.setState({ error: `${err}` }));
  };


  render() {
    const { className, game, ticket, download } = this.props;
    const { error } = this.state;
    /* <a href={getDownloadCardURL(game.pk, ticket.pk)}
      download={`Game ${game.id} - Ticket ${ticket.number}.pdf`}
      rel="_blank" type="application/pdf"
      className="btn btn-primary btn-lg">direct Download ticket {ticket.number}</a> */

    return (
      <div className={className || "view-ticket"}>
        {error && <div className="alert alert-warning" role="alert"><span className="error-message">{error}</span></div>}
        {download === true && <div className="download">
          <button className="btn btn-primary btn-lg" onClick={this.downloadPDF} >
            Download ticket {ticket.number}</button>
        </div>}
        <table className="bingo-ticket table table-striped table-bordered"
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
              <th colSpan={game.options.columns - 2} className="title">
                {game.title}
              </th>
              <th colSpan="2" className="number">
                Game {game.id} / Ticket {ticket.number}
              </th>
            </tr>
          </tfoot>
        </table>
        {ticket.error && <CardError error={ticket.error} />}
      </div>
    );
  }
}

export {
  BingoTicket,
};
