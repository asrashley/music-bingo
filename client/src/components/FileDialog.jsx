import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from './ModalDialog';

export class FileDialog extends React.Component {
  static propTypes = {
    accept: PropTypes.string.isRequired,
    onCancel: PropTypes.func.isRequired,
    onFileUpload: PropTypes.func.isRequired,
    title: PropTypes.string.isRequired,
    submit: PropTypes.string,
    backdrop: PropTypes.bool,
  };

  state = {
    file: null
  };

  onFormSubmit = (e) => {
    const { onFileUpload } = this.props;
    e.preventDefault();
    if (this.state.file) {
      onFileUpload(this.state.file);
    }
  }

  onChange = (e) => {
    this.setState({ file: e.target.files[0] });
  }

  render() {
    const { accept, backdrop, onCancel, title } = this.props;
    const { file } = this.state;
    const submit = this.props.submit || 'Select file';
    const footer = (
      <div>
        <button className="btn btn-primary yes-button"
          disabled={file===null}
          onClick={this.onFormSubmit} >{submit}</button>
        <button className="btn btn-secondary cancel-button"
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
          {this.props.children}
          <form onSubmit={this.onFormSubmit} method="POST">
            <input type="file" onChange={this.onChange} accept={accept} className="choose-file" />
          </form>
        </ModalDialog>
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </React.Fragment>
    );
  }
}
