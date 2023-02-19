import React from 'react';
import PropTypes from 'prop-types';
import log from 'loglevel';

import { ModalDialog } from '../../components';
import { RegisterForm } from '../../user/components';

import { UserPropType } from '../../user/types/User';

export class AddUserDialog extends React.Component {
  static propTypes = {
    onAddUser: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    backdrop: PropTypes.bool,
    users: PropTypes.arrayOf(UserPropType).isRequired
  };

  checkUser = ({ username, email }) => {
    const { users } = this.props;
    log.debug(`Check user ${username} ${email}`);
    return new Promise((resolve) => {
      for (let i = 0; i < users.length; ++i) {
        const user = users[i];
        log.trace(`${user.username} ${user.email}`);
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
