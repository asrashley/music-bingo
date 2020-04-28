import React from 'react';
import { ModalDialog } from '../../components';

export function LogoutDialog({ onCancel, onConfirm, backdrop }) {
  const footer = (
    <div>
      <button type="submit" className="btn btn-success login-button" onClick={onCancel} >No, I want to stay!</ button>
      <button type="submit" className="btn btn-danger login-button" onClick={onConfirm} >Yes, log out</ button>
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
      {backdrop === true && <div class="modal-backdrop fade show"></div> }
    </div>
  );
}