import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from '../../components';


export class FailedSelectionDialog extends React.Component {
  static propTypes = {
    ticket: PropTypes.object.isRequired,
    onCancel: PropTypes.func.isRequired,
  };

  render() {
    const { ticket, onCancel } = this.props;
    const footer = (
      <div>
        <button className="btn btn-primary"
          data-dismiss="modal" onClick={onCancel}>OK</button>
      </div>
    );
    return (
      <ModalDialog
        className="failed-select-ticket"
        id="fail-select"
        onCancel={onCancel}
        title="Sorry that ticket has already been taken"
        footer={footer}
      >
        <h3>It turns out you were too slow, and ticket {ticket.number} has already been taken</h3>
        <p >Hopefully you will have more luck with your next try.</p>
      </ModalDialog>
    );
  }
}
