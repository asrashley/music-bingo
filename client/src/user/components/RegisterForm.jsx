import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from "react-hook-form";
import log from 'loglevel';

import { Input } from '../../components';
import { minPasswordLength } from '../constants';
import { emailRules, usernameRules, passwordRules, passwordConfirmRules } from '../rules';

export function RegisterForm({ registerTitle = "Register", checkUser, onSubmit, onCancel }) {
  const { register, handleSubmit, formState, getValues, setError } = useForm({
    mode: 'onChange',
  });
  const { isSubmitting, isValid, errors } = formState;

  const submitWrapper = async (data) => {
    try {
      const result = await onSubmit(data);
      if (result === true) {
        return;
      }
      result.forEach((item) => {
        const { name } = item;
        setError(name, item);
      })

    } catch (err) {
      log.error(err);
      setError('username', err);
    }
  };
  return (
    <form onSubmit={handleSubmit(submitWrapper)} className="register-form" >
      <Input name="username"
        label="Username"
        register={register}
        rules={usernameRules(getValues, checkUser)}
        errors={errors}
        formState={formState}
        type="text"
        hint="This is the name you will use to log in and the name that will be visible to other players."
      />
      <Input name="email"
        label="Email address"
        register={register}
        rules={emailRules(getValues, checkUser)}
        errors={errors}
        formState={formState}
        type="text"
        hint="We'll never share your email with anyone else."
      />
      <Input type="password"
        className="password"
        register={register}
        rules={passwordRules(getValues)}
        label="Password"
        errors={errors}
        formState={formState}
        name="password"
        hint={`The password needs to be at least ${minPasswordLength} characters in length.`}
        required />
      <Input type="password"
        className="password"
        register={register}
        rules={passwordConfirmRules(getValues)}
        label="Confirm Password"
        name="confirmPassword"
        errors={errors}
        formState={formState}
        hint="Please enter the password a second time to make sure you have typed it correctly"
        required />
      <div className="form-text text-muted">* = a required field</div>
      <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={isSubmitting === true || isValid !== true}>{registerTitle}</button>
        <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

RegisterForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  checkUser: PropTypes.func.isRequired,
  registerTitle: PropTypes.string
};
