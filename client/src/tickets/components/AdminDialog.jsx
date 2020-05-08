import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { ModalDialog } from '../../components';
import routes from '../../routes';

export class AdminDialog extends React.Component {
  static propTypes = {
    game: PropTypes.object.isRequired,
    ticket: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired,
    onAdd: PropTypes.func.isRequired,
    onRelease: PropTypes.func.isRequired,
  };

  render() {
    const { ticket, game, user, onAdd, onCancel, onRelease } = this.props;
    let username = 'you';
    if (ticket.user && ticket.user !== user.pk) {
      username = user.users[ticket.user].username;
    }
    const footer = (
      <div>
        <Link to={reverse(`${routes.viewTicket}`, { gamePk: game.pk, ticketPk: ticket.pk })}
          className="btn btn-primary play-game">View Ticket</Link>
        {ticket.user && <button className="btn btn-primary yes-button"
          onClick={() => onRelease(ticket)} >Release Ticket</button>}
        {ticket.user === null && <button className="btn btn-primary yes-button"
          onClick={() => onAdd(ticket)} >Claim Ticket</button>}
        <button className="btn btn-secondary cancel-button"
          data-dismiss="modal" onClick={onCancel}>Cancel</button>
      </div>
    );
    return (
      <ModalDialog
        className="confirm-select-ticket"
        id="confirm-select"
        onCancel={onCancel}
        title={`Ticket ${ticket.number}`}
        footer={footer}
      >
        <h3>Ticket {ticket.number}</h3>
        {ticket.user && <p>This ticket is owned by {username}</p>}
      </ModalDialog>
    );
  }
}
