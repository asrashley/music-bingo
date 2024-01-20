import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from '../../components';

import { TicketPropType } from '../types/Ticket';
import { UserPropType } from '../../user/types/User';

export function AdminTicketDialog({ ticket, user, usersMap, onAdd, onCancel, onRelease, onView }) {
  let username = 'you';
  if (ticket.user > 0 && ticket.user !== user.pk) {
    username = usersMap[ticket.user].username;
  }
  const footer = (
    <div>
      <button
        className="btn btn-primary play-game"
        onClick={() => onView(ticket)}>View Ticket</button>
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
  ticket: TicketPropType.isRequired,
  user: UserPropType.isRequired,
  usersMap: PropTypes.object.isRequired,
  onCancel: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
  onRelease: PropTypes.func.isRequired,
  onView: PropTypes.func.isRequired,
};