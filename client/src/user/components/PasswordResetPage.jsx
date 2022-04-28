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
  const { alert, user, onCancel } = props;
  let className = "password-reset-form";

  const submitWrapper = (data) => {
    const { onSubmit } = props;
    return onSubmit(data).then(result => {
      if (result !== true && result !== undefined) {
        setError(result);
      }
    });
  };

  if (user.isFetching) {
    className += " submitting";
  }

  return (
    <form onSubmit={handleSubmit(submitWrapper)} className={className} >
      <h2>Request a password reset</h2>
      {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
      <Input name="email" label="Email address"
        type="email"
        register={register}
        rules={emailRules(getValues)}
        errors={errors}
        formState={formState}
        hint="This must be the email address you used when registering. This is why we asked for your email address when you registered!"
      />
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
  user: PropTypes.object.isRequired,
  alert: PropTypes.string,
};

class PasswordResetPage extends React.Component {
  static propTypes = {
    user: PropTypes.object.isRequired,
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };

  constructor(props) {
    super(props);
    this.state = {
      resetSent: false,
      alert: '',
    };
  }

  componentDidMount() {
    const { user } = this.props;
    if (user.error) {
      this.setState({alert: user.error});
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { user } = this.props;
    if (user.error !== this.state.alert) {
      this.setState({alert: user.error});
    }
  }

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
      .then((result) => {
        console.dir(result);
        if(result && result.payload){
          const { payload } = result;
          if(payload.success === true){
            this.setState({ resetSent: true, email });
            return true;
          }
          this.setState({alert: payload.error});
          return false;
        }
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
    const { user } = this.props;
    if (resetSent) {
      return (
        <div className="reset-sent">
          <h3>A password reset has been sent to {email}</h3>
          <p className="please-wait">Please wait for an email with instuctions on how to re-enable your account.</p>
        </div>
      );
    }
    return (
      <PasswordResetForm alert={alert} user={user} onSubmit={this.handleSubmit} onCancel={this.onCancel} />
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
