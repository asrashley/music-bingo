import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';


import { passwordResetUser } from '../userSlice';

import { getUser } from '../../user/userSelectors';

import routes from '../../routes';

import '../styles/user.scss';
import { PasswordResetForm } from './PasswordResetForm';
import { HistoryPropType } from '../../types/History';
import { UserPropType } from '../types/User';

export class PasswordResetPageComponent extends React.Component {
  static propTypes = {
    user: UserPropType.isRequired,
    dispatch: PropTypes.func,
    history: HistoryPropType.object,
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
        //console.error(err);
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
  return {
    user: getUser(state, ownProps),
  };
};

export const PasswordResetPage = connect(mapStateToProps)(PasswordResetPageComponent);
