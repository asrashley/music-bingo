import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { emailRules } from '../rules';
import { UserPropType } from '../types/User';

export function PasswordResetForm(props) {
  const { register, handleSubmit, formState, getValues, errors, setError } = useForm({
    mode: 'onSubmit',
  });
  const { alert, user, onCancel } = props;
  let className = "password-reset-form";

  const submitWrapper = (data) => {
    const { onSubmit } = props;
    return onSubmit(data).then(result => {
      if (result !== true && result !== undefined) {
        setError('email', result);
      }
    })
      .catch(err => {
        const error = (err ? `${err}` : 'Unknown error');
        setError('email', {
          type: "validate",
          message: error,
          name: "email",
        });
      });
  };

  if (user.isFetching) {
    className += " submitting";
  }

  return (
    <form onSubmit={handleSubmit(submitWrapper)} className={className}>
      <h2>Request a password reset</h2>
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input name="email"
        label="Email address"
        type="email"
        register={register}
        rules={emailRules(getValues)}
        errors={errors}
        formState={formState}
        hint="This must be the email address you used when registering. This is why we asked for your email address when you registered!" />
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary"
          disabled={user.isFetching}>Request Password Reset</button>
        <button type="cancel" name="cancel" className="btn btn-danger"
          disabled={user.isFetching} onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

PasswordResetForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  user: UserPropType.isRequired,
  alert: PropTypes.string,
};
