import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from './ModalDialog';

export function ConfirmDialog({ backdrop, changes, title, onCancel, onConfirm }) {
  if (title === undefined) {
    title = "Confirm save changes";
  }
  const footer = (
    <div>
      <button className="btn btn-primary yes-button" aria-label="Confirm"
        onClick={() => onConfirm(changes)} >Yes Please</button>
      <button className="btn btn-secondary cancel-button" aria-label="Cancel"
        data-dismiss="modal" onClick={onCancel}>Cancel</button>
    </div>
  );
  return (
    <React.Fragment>
      <ModalDialog
        className="confirm-save-changes"
        onCancel={onCancel}
        title={title}
        footer={footer}
      >
        <h3>Would you like to save the following changes?</h3>
        <ul className="changes-list">
          {changes.map((change, idx) => <li key={idx}>{change}</li>)}
        </ul>
      </ModalDialog>
      {backdrop === true && <div className="modal-backdrop fade show"></div>}
    </React.Fragment>
  );
}

ConfirmDialog.propTypes = {
  changes: PropTypes.array.isRequired,
  onCancel: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  title: PropTypes.string,
  backdrop: PropTypes.bool,
};

