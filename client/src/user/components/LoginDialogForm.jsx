import React from 'react';
import PropTypes from 'prop-types';

import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";
import { Input, ModalDialog } from '../../components';
import { routes } from '../../routes/routes';
import { loginUsernameRules, passwordRules } from '../rules';
import { UserPropType } from '../types/User';

function LoginFooter({ user, playAsGuest, isSubmitting }) {
  const showCreateGuest = (playAsGuest && user.guest.valid &&
    !(user.guest.username && user.guest.password));
  let buttonText = 'Login';
  if (user.isFetching === true) {
    buttonText = 'Checking..';
  } else if (isSubmitting) {
    buttonText = 'Logging in..';
  } return (
    <React.Fragment>
      <div className="row mb-2 mt-3">
        <p className="password-reset col-8">
          <Link to={reverse(`${routes.passwordReset}`)}>Help, I have forgotten my password!</Link>
        </p>
        <span className="col-4 pr-4">
          {showCreateGuest && <button onClick={playAsGuest}
            className="btn btn-primary guest-button"
            disabled={user.isFetching || isSubmitting}>Play as a guest</button>}
          <button type="submit" aria-label="Submit" className="btn btn-success btn-lg login-button"
            disabled={user.isFetching || isSubmitting}>{buttonText}</button>
        </span>
      </div>
      <div className="row border-top pt-3 pb-2 create-account">
        <span className="col-5 text-center">
          <Link className="btn btn-primary register-button"
            disabled={user.isFetching}
            to={reverse(`${routes.register}`)}>Create an account</Link>
        </span>
        <span className="col-7">
          It is free and we won&apos;t pass on your details to anyone else.
        </span>
      </div>
    </React.Fragment>
  );
}
LoginFooter.propTypes = {
  user: UserPropType.isRequired,
  playAsGuest: PropTypes.func,
  isSubmitting: PropTypes.bool
};

function LoginAlert({ alert }) {
  if (!alert) {
    return null;
  }
  return <div className="alert alert-warning" role="alert">
    <span className="error-message">{alert}</span>
  </div>;
}
LoginAlert.propTypes = {
  alert: PropTypes.string,
};

export function LoginDialogForm({ alert, onCancel, user, playAsGuest, className, onSubmit }) {
  const { register, handleSubmit, formState, errors, getValues } = useForm({
    mode: 'onChange',
    defaultValues: {
      username: user.username || user.guest.username,
      password: user.password || user.guest.password,
    }
  });
  const { isSubmitting } = formState;

  const submitWrapper = (data) => onSubmit(data);
  if (className === undefined) {
    className = '';
  }
  if (user.isFetching === true || isSubmitting) {
    className += ' submitting';
  }
  return (
    <form onSubmit={handleSubmit(submitWrapper)} className={className}>
      <ModalDialog id="login"
        title="Log into Musical Bingo"
        footer={<LoginFooter user={user} playAsGuest={playAsGuest} isSubmitting={isSubmitting} />}
        onCancel={onCancel}
      >
        <LoginAlert alert={alert} />
        <Input type="text" className="username"
          register={register}
          rules={loginUsernameRules(getValues)}
          label="User name or email address"
          errors={errors}
          formState={formState}
          hint="This is the name you used when you registered your account"
          name="username" required />
        <Input type="password"
          className="password"
          register={register}
          rules={passwordRules(getValues)}
          errors={errors}
          formState={formState}
          label="Password"
          name="password"
          required />
        <div className="form-check">
          <input
            id="rememberMe"
            className="form-check-input"
            type="checkbox"
            {...register("rememberme")} />
          <label className="form-check-label" htmlFor="rememberMe">
            Remember me
          </label>
        </div>
      </ModalDialog>
    </form>
  );
}
LoginDialogForm.propTypes = {
  alert: PropTypes.string,
  className: PropTypes.string,
  user: UserPropType.isRequired,
  playAsGuest: PropTypes.func,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};
