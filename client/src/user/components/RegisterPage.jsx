import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { checkUser, registerUser } from '../userSlice';
import { minPasswordLength } from '../constants';
import { emailRules, usernameRules, passwordRules, passwordConfirmRules } from '../rules';
import routes from '../../routes';

import '../styles/user.scss';

function RegisterForm(props) {
  const { register, handleSubmit, formState, getValues, errors, setError } = useForm({
    mode: 'onChange',
  });
  const { checkUser, onSubmit, onCancel } = props;
  const { isSubmitting } = formState;

  const submitWrapper = (data) => {
    return onSubmit(data).then(result => {
      if (result !== true) {
        setError(result);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit(submitWrapper)} className="register-form" >
      <Input name="username" label="Username"
        register={register(usernameRules(getValues, checkUser))}
        errors={errors}
        formState={formState}
        type="text"
        hint="This is the name you will use to log in and the name that will be visible to other players."
      />
      <Input name="email" label="Email address"
        register={register(emailRules(getValues, checkUser))}
        errors={errors}
        formState={formState}
        type="text"
        hint="We'll never share your email with anyone else."
         />
      <Input type="password" className="password"
        register={register(passwordRules(getValues))}
        label="Password"
        errors={errors}
        formState={formState}
        name="password"
        hint={`The password needs to be at least ${minPasswordLength} characters in length.`}
        required />
      <Input type="password" className="password"
        register={register(passwordConfirmRules(getValues))}
        label="Confirm Password"
        name="confirmPassword"
        errors={errors}
        formState={formState}
        hint="Please enter the password a second time to make sure you have typed it correctly"
        required />
      <div className="form-text text-muted">* = a required field</div>
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>Register</button>
        <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
      </div>

    </form>
  );
}

RegisterForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  checkUser: PropTypes.func.isRequired,
};

class RegisterPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };


  handleSubmit = ({ email, password, username }) => {
    const { dispatch } = this.props;
    return dispatch(registerUser({ email, password, username })).then(this.submitResponse);
  };

  submitResponse = (result) => {
    const { success, error } = result;
    const { history } = this.props;
    if (success === true) {
      history.push(reverse(`${routes.index}`));
      return true;
    }

    const errs = [];
    for (let name in error) {
      if (error[name]) {
        errs.push({
          type: "validate",
          message: error[name],
          name,
        });
      }
    }
    if (errs.length === 0) {
      return(error);
    }
    return(errs);
  };

  onCancel = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.login}`));
  };

  checkUser = ({ email, username }) => {
    const { dispatch } = this.props;
    return dispatch(checkUser({ email, username }));
  }

  render() {
    return (
      <RegisterForm {...this.props} onSubmit={this.handleSubmit} onCancel={this.onCancel}
        checkUser={this.checkUser}
      />
    );
  }
};

RegisterPage = connect()(RegisterPage);

export {
  RegisterPage
};
