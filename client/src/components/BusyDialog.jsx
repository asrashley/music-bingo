import React from 'react';
import PropTypes from 'prop-types';
import { ModalDialog } from './ModalDialog';

export class BusyDialog extends React.Component {
  static propTypes = {
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    backdrop: PropTypes.bool,
  };

  render() {
    const { backdrop, onClose, text, title } = this.props;
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
          {this.props.children}
          {text}
        </ModalDialog>
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </React.Fragment>
    );
  }
}
