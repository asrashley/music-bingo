import React from 'react';
import PropTypes from 'prop-types';
import { CircularProgressbar } from 'react-circular-progressbar';

import { ModalDialog } from './ModalDialog';
import { ImportTablePropType } from '../admin/types/Importing';

import 'react-circular-progressbar/dist/styles.css';

export function ProgressDialog({ added, backdrop, children, onCancel, onClose, errors, pct,
  text, title, done }) {
  const pctText = `${Math.floor(pct)}%`;
  let footer, result;
  if (done === true) {
    footer = (
      <div>
        <button className="btn btn-primary close-button"
          aria-label="Close"
          data-dismiss="modal" onClick={onClose}>Close</button>
      </div>
    );
  } else {
    footer = (
      <div>
        <button className="btn btn-secondary cancel-button"
          aria-label="Cancel"
          data-dismiss="modal" onClick={onCancel}>Cancel</button>
      </div>
    );
  }
  if (added.length > 0) {
    result = (
      <div className="added-items">
        <p>Added:</p>
        <ul>
          {added.map((table, idx) => (
            <li key={idx}>{table.count} {table.name}</li>
          ))}
        </ul>
      </div>
    );
  } else {
    result = <React.Fragment />;
  }
  return (
    <React.Fragment>
      <ModalDialog
        className="progress-dialog"
        onCancel={(done === true) ? onClose : onCancel}
        title={title}
        footer={footer}
      >
        {children}
        <div className="progress-wrapper">
          <CircularProgressbar value={pct} text={pctText} />
        </div>
        <p className="progress-text">{text}</p>
        {errors.map((err, idx) => (
          <div key={idx} className="alert alert-warning" role="alert">
            <span className="error-message">{err}</span>
          </div>
        ))}
        {result}
      </ModalDialog>
      {backdrop === true && <div className="modal-backdrop fade show"></div>}
    </React.Fragment>
  );
}

ProgressDialog.propTypes = {
  added: PropTypes.arrayOf(ImportTablePropType).isRequired,
  errors: PropTypes.array.isRequired,
  text: PropTypes.string.isRequired,
  pct: PropTypes.number.isRequired,
  phase: PropTypes.number,
  numPhases: PropTypes.number,
  done: PropTypes.bool,
  onCancel: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  backdrop: PropTypes.bool,
};
