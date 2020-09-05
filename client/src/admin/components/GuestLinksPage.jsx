import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { Link } from 'react-router-dom';

import { DateTime } from '../../components';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import {
  fetchGuestLinksIfNeeded, createGuestToken, deleteGuestToken,
  invalidateGuestTokens
} from '../adminSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';
import { getGuestTokens, getAdminUserPk } from '../adminSelectors';

/* data */
import { initialState } from '../../app/initialState';
import routes from '../../routes';

function TableRow({token, onDelete}) {
  const link = reverse(`${routes.guestAccess}`, { token:token.jti});
  return (
    <tr>
      <td className="link">
        <Link to={link}>{link}</Link>
      </td>
      <td className="expires"><DateTime date={token.expires}/></td>
      <td className="delete">
        <button className="btn btn-warning"
        onClick={() => onDelete(token)}>Delete</button>
      </td>
    </tr>
  );
}

class GuestLinksPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch, user } = this.props;
    dispatch(fetchUserIfNeeded());
    if(user.loggedIn) {
      dispatch(fetchGuestLinksIfNeeded());
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user, userPk } = this.props;
    if (userPk !== prevProps.userPk && user.loggedIn) {
      console.log(`user.pk=${user.pk}`);
      dispatch(fetchGuestLinksIfNeeded());
    }
  }

  addLink = () => {
    const { dispatch } = this.props;
    dispatch(createGuestToken());
  }

  deleteLink = (token) => {
    const { dispatch } = this.props;
    dispatch(deleteGuestToken(token.jti));
  }

  refreshTokenList = () => {
    const { dispatch } = this.props;
    dispatch(invalidateGuestTokens());
    dispatch(fetchGuestLinksIfNeeded());
  }

  render() {
    const { tokens } = this.props;
    return(
      <div className="guest-tokens">
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th className="link">Link</th>
              <th className="expires">Expires</th>
              <th className="delete">
                Delete
                <button className="btn btn-light refresh-icon btn-sm float-right"
                        onClick={this.refreshTokenList}>&#x21bb;</button>
              </th>
            </tr>
          </thead>
          <tbody>
            {tokens.map((token, idx) => <TableRow key={idx} token={token} onDelete={this.deleteLink}/>)}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan="3">
                <button className="btn btn-primary" onClick={this.addLink}>Add link</button>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
    state = state || initialState;
    return {
      user: getUser(state, props),
      tokens: getGuestTokens(state, props),
      userPk: getAdminUserPk(state, props),
    };
  };

 GuestLinksPage = connect(mapStateToProps)(GuestLinksPage);

  export { GuestLinksPage };
