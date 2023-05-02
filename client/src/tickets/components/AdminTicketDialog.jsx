import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { ModalDialog } from '../../components';
import routes from '../../routes';

import { GamePropType } from '../../games/types/Game';
import { TicketPropType } from '../types/Ticket';
import { UserPropType } from '../../user/types/User';

export function AdminTicketDialog({ ticket, game, user, usersMap, onAdd, onCancel, onRelease }) {
  let username = 'you';
  if (ticket.user > 0 && ticket.user !== user.pk) {
    username = usersMap[ticket.user].username;
  }
  const footer = (
    <div>
      <Link to={reverse(`${routes.viewTicket}`, { gameId: game.id, ticketPk: ticket.pk })}
        className="btn btn-primary play-game">View Ticket</Link>
      {ticket.user && <button className="btn btn-primary yes-button"
        onClick={() => onRelease(ticket)} >Release Ticket</button>}
      {ticket.user <= 0 && <button className="btn btn-primary yes-button"
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
      {ticket.user > 0 && <p>This ticket is owned by {username}</p>}
    </ModalDialog>
  );
}

AdminTicketDialog.propTypes = {
  game: GamePropType.isRequired,
  ticket: TicketPropType.isRequired,
  user: UserPropType.isRequired,
  usersMap: PropTypes.object.isRequired,
  onCancel: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
  onRelease: PropTypes.func.isRequired,
};