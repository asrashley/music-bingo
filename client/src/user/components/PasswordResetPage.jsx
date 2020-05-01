import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { passwordResetUser } from '../userSlice';
import { emailRules } from '../rules';
import routes from '../../routes';

import '../styles/user.scss';

function PasswordResetForm(props) {
  const { register, handleSubmit, formState, getValues, errors, setError } = useForm({
    mode: 'onSubmit',
  });
  const { alert, onCancel } = props;
  const { isSubmitting } = formState;

  const submitWrapper = (data) => {
    const { onSubmit } = props;
    return onSubmit(data).then(result => {
      if (result !== true) {
        setError(result);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit(submitWrapper)} className="password-reset-form" >
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input name="email" label="Email address"
        register={register(emailRules(getValues))}
        errors={errors}
        formState={formState}
        hint="This must be the email you used when registering"
      />
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>Request Password Reset</button>
        <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

PasswordResetForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  alert: PropTypes.string,
};

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
    return dispatch(passwordResetUser({ email })).then(this.submitResponse);
  };

  submitResponse = (result) => {
    const { success, email, error } = result;
    if (success === true) {
      this.setState({ resetSent: true, email });
      return true;
    }
    this.setState({ alert: error || 'Unknown error'});
    return {
      type: "validate",
      message: error || 'Unknown error',
      name: "email",
    };

  };

  onCancel = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.login}`));
  };

  render() {
    const { alert, email, resetSent } = this.state;
    if (resetSent) {
      return (
        <div className="reset-sent">
          <h3>A password reset has been sent for {email}</h3>
          <p className="please-wait">Please wait for an email with instuctions on how to re-enable your account.</p>
        </div>
      );
    }
    return (
      <PasswordResetForm alert={alert} onSubmit={this.handleSubmit} onCancel={this.onCancel} />
    );
  }
};

PasswordResetPage = connect()(PasswordResetPage);

export {
  PasswordResetPage
};
