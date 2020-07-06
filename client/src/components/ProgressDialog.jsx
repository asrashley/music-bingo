import React from 'react';
import PropTypes from 'prop-types';
import { CircularProgressbar } from 'react-circular-progressbar';

import { ModalDialog } from './ModalDialog';

import 'react-circular-progressbar/dist/styles.css';

export class ProgressDialog extends React.Component {
  static propTypes = {
    added: PropTypes.array.isRequired,
    errors: PropTypes.array.isRequired,
    text: PropTypes.string.isRequired,
    pct: PropTypes.number.isRequired,
    phase: PropTypes.number,
    numPhases: PropTypes.number,
    done: PropTypes.bool,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string.isRequired,
    backdrop: PropTypes.bool,
  };

  render() {
    const { added, backdrop, onClose, errors, pct,
      text, title, done } = this.props;
    const pctText = `${Math.floor(pct)}%`;
    let footer;
    if (done === true) {
      footer = (
        <div>
          <button className="btn btn-primary close-button"
            data-dismiss="modal" onClick={onClose}>Close</button>
        </div>
      );
    } else {
      footer = (
        <div>
          <button className="btn btn-secondary cancel-button"
            data-dismiss="modal" onClick={onClose}>Cancel</button>
        </div>
      );
    }
    return (
      <React.Fragment>
        <ModalDialog
          className="progress-dialog"
          onCancel={onClose}
          title={title}
          footer={footer}
        >
          {this.props.children}
          <div className="progress-wrapper">
            <CircularProgressbar value={pct} text={pctText} />
          </div>
          <p className="progress-text">{text}</p>
          {errors.map((err, idx) => (
            <div key={idx} className="alert alert-warning" role="alert">
              <span className="error-message">{err}</span>
            </div>
          ))}
          {added.map((table, idx) => (
            <p key={idx} className="added-items">Added {table.count} {table.name}</p>
            ))}
        </ModalDialog>
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </React.Fragment>
    );
  }
}
