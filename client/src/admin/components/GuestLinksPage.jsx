import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { Link } from 'react-router-dom';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchGuestLinksIfNeeded } from '../adminSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';
import { getGuestTokens} from '../adminSelectors';

/* data */
import { initialState } from '../../app/initialState';
import routes from '../../routes';

function TableRow({token, onDelete}) {
  const link = reverse(`${routes.guestAccess}`, { token:token.token});
  return (
    <tr>
      <td className="link">
        <Link to={link}>{link}</Link>
      </td>
      <td className="expires">{token.expires}</td>
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
  
    render() {
        const { tokens } = this.props;
        return(
        <div className="guest-tokens">
          <table className="table table-striped table-bordered">
          <thead><tr>
            <th className="link">Link</th>
            <th className="expires">Expires</th>
            <th className="delete">Delete</th>
          </tr></thead>
          <tbody>
            {tokens.map((token, idx) => <TableRow key={idx} token={token}/>)}
          </tbody>
          </table>
        </div>);
    }
}  

const mapStateToProps = (state, props) => {
    state = state || initialState;
    return {
      user: getUser(state, props),
      tokens: getGuestTokens(state, props),
    };
  };
  
 GuestLinksPage = connect(mapStateToProps)(GuestLinksPage);
  
  export { GuestLinksPage };
  