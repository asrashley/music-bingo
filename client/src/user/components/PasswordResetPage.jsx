import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';

import { passwordResetUser } from '../userSlice';

import { getUser } from '../../user/userSelectors';

import { emailRules } from '../rules';
import routes from '../../routes';
import { initialState } from '../../app/initialState';

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
      <h2>Request a password reset</h2>
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input name="email" label="Email address"
        type="email"
        register={register(emailRules(getValues))}
        errors={errors}
        formState={formState}
        hint="This must be the email address you used when registering. This is why we asked for your email address when you registered!"
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
    user: PropTypes.object.isRequired,
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };

  state = {
    resetSent: false,
    alert: '',
  };

  handleSubmit = ({ email }) => {
    const { dispatch, user } = this.props;
    if (user.isFetching === true) {
      return {
        type: "validate",
        message: "Password reset already is in progress",
        name: "email",
      };
    }
    if (user.pk > 0 && user.error === null) {
      return {
        type: "validate",
        message: "User is currently logged in",
        name: "email",
      };
    }
    return dispatch(passwordResetUser({ email }))
      .then(() => {
        this.setState({ resetSent: true, email });
        return true;
      })
      .catch(err => {
        console.error(err);
        if (err.error) {
          err = err.error;
        }
        this.setState({ alert: `${err}` });
        return {
          type: "validate",
          message: `${err}`,
          name: "email",
        };
      });
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
          <h3>A password reset has been sent to {email}</h3>
          <p className="please-wait">Please wait for an email with instuctions on how to re-enable your account.</p>
        </div>
      );
    }
    return (
      <PasswordResetForm alert={alert} onSubmit={this.handleSubmit} onCancel={this.onCancel} />
    );
  }
};

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    user: getUser(state, ownProps),
  };
};

PasswordResetPage = connect(mapStateToProps)(PasswordResetPage);

export {
  PasswordResetPage
};
