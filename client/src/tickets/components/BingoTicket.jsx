import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { saveAs } from 'file-saver';

import { fetchCardIfNeeded,  setChecked } from '../../cards/cardsSlice';
import { getCard } from '../../cards/cardsSelectors';
import { initialState } from '../../app/initialState';
import { getDownloadCardURL } from '../../endpoints';

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
    card: PropTypes.object.isRequired,
    game: PropTypes.object.isRequired,
    ticket: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch, game, ticket } = this.props;
    dispatch(fetchCardIfNeeded(game.pk, ticket.pk));
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, game, ticket } = this.props;
    if (prevProps.game.pk !== game.pk ||
      prevProps.ticket.pk !== ticket.pk) {
      dispatch(fetchCardIfNeeded(game.pk, ticket.pk));
    }
  }

  onClickCell = (cell) => {
    const { game, ticket, dispatch } = this.props;
    const { row, column } = cell;

    dispatch(setChecked({
      gamePk: game.pk,
      ticketPk: ticket.pk,
      row,
      column,
      checked: !cell.checked
    }));
  };

  downloadPDF = (ev) => {
    const { game, ticket } = this.props;
    return fetch(getDownloadCardURL(game.pk, ticket.pk), {
      credentials: 'same-origin',
      header: {
        Accept: "application/pdf",
      }
    })
      .then((response) => {
        if (!response.ok) {
          return Promise.reject({ error: `${response.status}: ${response.statusText}` });
        }
        const filename = `Game ${game.id} - Ticket ${ticket.number}.pdf`;
        return response.blob().then(blob => {
          saveAs(blob, filename);
          return filename;
        });
      });
  };


  render() {
    const { game, ticket, card, user } = this.props;
    /* <a href={getDownloadCardURL(game.pk, ticket.pk)}
      download={`Game ${game.id} - Ticket ${ticket.number}.pdf`}
      rel="_blank" type="application/pdf"
      className="btn btn-primary btn-lg">direct Download ticket {ticket.number}</a> */

    return (
      <div className="view-ticket">
        <div className="download">
          <button className="btn btn-primary btn-lg" onClick={this.downloadPDF} >
            Download ticket {ticket.number}</button>
        </div>
        <table className="bingo-ticket table table-striped table-bordered"
          data-game-id={game.id} data-ticket-number={ticket.number}>
          <thead>
            <tr>
              <th colSpan={user.options.columns} className="logo">
              </th>
            </tr>
          </thead>
          <tbody>
            {card.rows.map((row, idx) => <TableRow key={idx} row={row} options={user.options} onClick={this.onClickCell} />)}
          </tbody>
          <tfoot>
            <tr>
              <th colSpan={user.options.columns - 2} className="title">
                {game.title}
              </th>
              <th colSpan="2" className="number">
                Game {game.id} / Ticket {ticket.number}
              </th>
            </tr>
          </tfoot>
        </table>
        {card.error && <CardError error={card.error} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { game, ticket } = ownProps;
  return {
    game,
    ticket,
    card: getCard(state, ownProps),
  };
};

BingoTicket = connect(mapStateToProps)(BingoTicket);

export {
  BingoTicket,
};