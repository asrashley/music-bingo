import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { reduxForm, Field } from 'redux-form';

import { Input } from '../../components';
import { validatePasswordResetForm } from '../rules';
import { passwordResetUser} from '../userSlice';

import routes from '../../routes';

import '../styles/user.scss';

class PasswordResetForm extends React.Component {
  static propTypes = {
    handleSubmit: PropTypes.func.isRequired,
    submitting: PropTypes.bool,
    pristine: PropTypes.bool,
    valid: PropTypes.bool,
  };

  render() {
    const { alert, handleSubmit, submitting, pristine, valid, onCancel } = this.props;
    return (
      <form onSubmit={handleSubmit} className="password-reset-form" >
        {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
        <Field name="email" label="Email address"
          component={Input}
          hint="This must be the email you used when registering"
          required />
        <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={pristine || submitting || !valid}>Request Password Reset</button>
          <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
          </div>

      </form>
    );
  }
}

PasswordResetForm = reduxForm({
  form: 'PasswordReset',
  validate: validatePasswordResetForm,
})(PasswordResetForm);

class PasswordResetPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };

  state = {
    resetSent: false,
    alert: '',
  };

  handleSubmit = ({ email }) => {
    const { dispatch } = this.props;
    dispatch(passwordResetUser({ email })).then(this.submitResponse);
  }

  submitResponse = (result) => {
    const { success, email, error } = result;
    if (success === true) {
      this.setState({ resetSent: true, email });
    } else if (error === undefined) {
      this.setState({ alert: 'Unknown error' });
    } else {
      this.setState({ alert: error });
    }
  }

  onCancel = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.login}`));
  }

  render() {
    const { alert, email, resetSent } = this.state;
    if (resetSent) {
      return (
        <div className="reset-sent">
          <h3>A password reset has been sent for {email}</h3>
          <p className="please-wait">Please wait for an email with instuctions if how to re-enable your account.</p>
        </div>
        );
    }
    return (
      <PasswordResetForm alert={alert} onSubmit={this.handleSubmit} onCancel={this.onCancel}/>
    );
  }
};

PasswordResetPage = connect()(PasswordResetPage);

export {
  PasswordResetPage
};
