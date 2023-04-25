import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from '../../components';

import { TicketPropType } from '../types/Ticket';
import { UserPropType } from '../../user/types/User';

export function ConfirmSelectionDialog({ ticket, user, onCancel, onConfirm }) {
  const mode = ticket.user ? "release" : "choose";
  let username = 'you';
  if (ticket.user && ticket.user !== user.pk && user.groups.admin === true) {
    username = user.users[ticket.user].username;
  }
  const warning = ticket.user ?
    `This ticket is owned by ${username}` :
    "Once you click yes, there is no way back and you cannot undo your selection!";
  const footer = (
    <div>
      <button className="btn btn-primary yes-button"
        onClick={() => onConfirm(ticket)} >Yes Please</button>
      <button className="btn btn-secondary cancel-button"
        data-dismiss="modal" onClick={onCancel}>Cancel</button>
    </div>
  );
  return (
    <ModalDialog
      className="confirm-select-ticket"
      id="confirm-select"
      onCancel={onCancel}
      title={ticket.user ? "Confirm release ticket" : "Confirm ticket choice"}
      footer={footer}
    >
      <h3>Would you like to {mode} ticket {ticket.number}?</h3>
      <p className="warning">{warning}</p>
    </ModalDialog>
  );
}

ConfirmSelectionDialog.propTypes = {
  ticket: TicketPropType.isRequired,
  user: UserPropType.isRequired,
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
};

