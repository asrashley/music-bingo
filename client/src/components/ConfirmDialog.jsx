import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from './ModalDialog';

export class ConfirmDialog extends React.Component {
  static propTypes = {
    changes: PropTypes.array.isRequired,
    onCancel: PropTypes.func.isRequired,
    onConfirm: PropTypes.func.isRequired,
    title: PropTypes.string.isRequired,
    backdrop: PropTypes.bool,
  };

  render() {
    const { backdrop, changes, onCancel, onConfirm } = this.props;
    const footer = (
      <div>
        <button className="btn btn-primary yes-button"
          onClick={() => onConfirm(changes)} >Yes Please</button>
        <button className="btn btn-secondary cancel-button"
          data-dismiss="modal" onClick={onCancel}>Cancel</button>
      </div>
    );
    return (
      <React.Fragment>
        <ModalDialog
          className="confirm-save-changes"
          onCancel={onCancel}
          title="Confirm save changes"
          footer={footer}
        >
          <h3>Would you like to save the following changes?</h3>
          <ul>
            {changes.map((change, idx) => <li key={idx}>{change}</li>)}
          </ul>
        </ModalDialog>
        {backdrop === true && <div className="modal-backdrop fade show"></div> }
      </React.Fragment>
    );
  }
}
