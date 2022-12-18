import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";

import { Input } from '../../components';

import { emailRules, passwordRules, passwordConfirmRules } from '../rules';
import { minPasswordLength } from '../constants';

export function PasswordChangeForm({ alert, onSubmit, onCancel, token, user, passwordReset }) {
  const { register, handleSubmit, formState, getValues, errors, setError } = useForm({
    mode: 'onChange',
    defaultValues: {
      token,
      email: user ? user.email : '',
    }
  });
  const { isSubmitting } = formState;

  const emailHint = passwordReset ?
    "The email address you used when you registered your account" :
    "Either your currently registere email address or the new email address to use";
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
      <Input
        name="email"
        label="Email address"
        register={register}
        rules={emailRules()}
        errors={errors}
        required
        formState={formState}
        type="text"
        hint={emailHint}
      />
      {token && <input
                  type="hidden"
                  { ...register('token', { value: token}) } />}
      {!passwordReset && <Input
                           type="password"
                           className="password"
                           register={register}
                           rules={passwordRules(getValues)}
        label="Existing Password"
        placeholder="Your current password"
        errors={errors}
        formState={formState}
        name="existingPassword"
        hint="Your current password"
        required />}
      <Input
        type="password"
        className="password"
        register={register}
        rules={passwordRules(getValues)}
        label="New Password"
        placeholder="Choose a new password"
        errors={errors}
        formState={formState}
        name="password"
        hint={`The password needs to be at least ${minPasswordLength} characters in length.`}
        required />
      <Input
        type="password"
        className="password"
        register={register}
        rules={passwordConfirmRules(getValues)}
        label="Confirm New Password"
        name="confirmPassword"
        errors={errors}
        formState={formState}
        hint="Please enter the password a second time to make sure you have typed it correctly"
        required />
      <div className="form-text text-muted">* = a required field</div>
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {passwordReset ? "Reset Password" : "Change password"}
        </button>
        <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
      </div>

    </form>
  );
}

PasswordChangeForm.propTypes = {
  alert: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  passwordReset: PropTypes.bool,
  token: PropTypes.string,
  user: PropTypes.object,
};
