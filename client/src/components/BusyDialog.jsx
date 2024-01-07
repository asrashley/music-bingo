import React from 'react';
import PropTypes from 'prop-types';
import { ModalDialog } from './ModalDialog';

export function BusyDialog({ backdrop, onClose, text = '', title, children }) {
  const footer = (
    <div>
      <button className="btn btn-secondary cancel-button"
        data-dismiss="modal" onClick={onClose}>Cancel</button>
    </div>
  );

  return (
    <React.Fragment>
      <ModalDialog
        className="busy-dialog"
        onCancel={onClose}
        title={title}
        footer={footer}
      >
        {children}
        {text}
      </ModalDialog>
      {backdrop === true && <div className="modal-backdrop fade show"></div>}
    </React.Fragment>
  );
}
BusyDialog.propTypes = {
  children: PropTypes.node,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  text: PropTypes.string,
  backdrop: PropTypes.bool,
};

