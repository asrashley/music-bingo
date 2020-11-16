import React from 'react';
import PropTypes from 'prop-types';

import { ModalDialog } from '../../components';
import { RegisterForm } from '../../user/components';

export class AddUserDialog extends React.Component {
  static propTypes = {
    onAddUser: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    backdrop: PropTypes.bool,
    users: PropTypes.array.isRequired
  };

  checkUser = ({ username, email }) => {
    const { users } = this.props;

    return new Promise((resolve) => {
      for (let i = 0; i < users.length; ++i) {
        const user = users[i];
        if (user.username === username) {
          resolve({ "username": true });
          return;
        }
        if (user.email === email) {
          resolve({ "email": true });
          return;
        }
      }
      resolve(true);
    });
  };

  render() {
    const { backdrop, onAddUser, onClose } = this.props;

    return (
      <React.Fragment>
        <ModalDialog
          className="add-user"
          onCancel={onClose}
          title="Add User"
          footer={<div />}
        >
          <RegisterForm
            onSubmit={onAddUser}
            onCancel={onClose}
            registerTitle="Add"
            checkUser={this.checkUser} />
        </ModalDialog>
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </React.Fragment>
    );
  }
}
