import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { passwordResetUser } from '../userSlice';
import { emailRules, passwordRules, passwordConfirmRules } from '../rules';
import routes from '../../routes';
import { minPasswordLength } from '../constants';
import { initialState } from '../../app/initialState';

import '../styles/user.scss';

function PasswordChangeForm({ alert, onSubmit, onCancel, token }) {
  const { register, handleSubmit, formState, getValues, errors, setError } = useForm({
    mode: 'onChange',
    defaultValues: {
      token,
    }
  });
  const { isSubmitting } = formState;

  const submitWrapper = (data) => {
    return onSubmit(data).then(result => {
      if (result !== true) {
        setError(result);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit(submitWrapper)} className="change-password-form" >
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input name="email" label="Email address"
        register={register(emailRules())}
        errors={errors}
        required
        formState={formState}
        type="text"
        hint="The email address you used to register"
      />
      <input name="token" type="hidden" value={token} ref={register} />
      <Input type="password" className="password"
        register={register(passwordRules(getValues))}
        label="New Password"
        placeholder="Choose a new password"
        errors={errors}
        formState={formState}
        name="password"
        hint={`The password needs to be at least ${minPasswordLength} characters in length.`}
        required />
      <Input type="password" className="password"
        register={register(passwordConfirmRules(getValues))}
        label="Confirm New Password"
        name="confirmPassword"
        errors={errors}
        formState={formState}
        hint="Please enter the password a second time to make sure you have typed it correctly"
        required />
      <div className="form-text text-muted">* = a required field</div>
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>Reset Password</button>
        <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
      </div>

    </form>
  );
}

class PasswordResetConfirmPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };

  state = {
    resetSent: false,
    alert: '',
  };

  onSubmit = (values) => {
    const { dispatch } = this.props;
    return dispatch(passwordResetUser(values))
      .then(() => {
        const { history } = this.props;
        history.push(reverse(`${routes.index}`));
        return true;
      })
      .catch(err => {
        const error = (err ? `${err}` : 'Unknown error');
        this.setState({ alert: error });
        return {
          type: "validate",
          message: error,
          name: "email",
        };
      });
  };

  onCancel = (ev) => {
    const { history } = this.props;
    ev.preventDefault();
    history.push(reverse(`${routes.login}`));
    return false;
  };

  render() {
    const { alert } = this.state;
    const { token } = this.props;
    return (
      <div className="reset-sent">
        <PasswordChangeForm alert={alert} onSubmit={this.onSubmit}
          onCancel={this.onCancel} token={token} />
      </div>
    );
  }
};

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;

  const { token } = ownProps.match.params;
  return {
    token
  }
}

PasswordResetConfirmPage = connect(mapStateToProps)(PasswordResetConfirmPage);

export {
  PasswordResetConfirmPage
};
