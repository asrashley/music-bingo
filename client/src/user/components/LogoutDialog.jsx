import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from '../../components';

export function LogoutDialog({ onCancel, onConfirm, backdrop }) {
  const footer = (
    <div>
      <button type="button" className="btn btn-success login-button" onClick={onCancel} >No, I want to stay!</ button>
      <button type="button" className="btn btn-danger login-button" onClick={onConfirm} >Yes, log out</ button>
    </div>
  );

  return (
    <div>
      <ModalDialog id="logout"
        title="Logout from Musical Bingo?"
        footer={footer} onCancel={onCancel}>
        <h3>
          Would you like to log out?
        </h3>
      </ModalDialog>
      {backdrop === true && <div className="modal-backdrop fade show"></div>}
    </div>
  );
}
LogoutDialog.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  backdrop: PropTypes.bool
};