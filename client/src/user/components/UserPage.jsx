import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

/* components */
import { AdminGameActions } from '../../games/components/AdminGameActions';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';
import { getDatabaseImportState } from '../../admin/adminSelectors';
import { getGameImportState } from '../../games/gamesSelectors';

/* data */
import routes from '../../routes';
import { initialState } from '../../app/initialState';

import '../styles/user.scss';

class UserPage extends AdminGameActions {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  render() {
    const { user, databaseImporting, gameImporting } = this.props;
    const { ActiveDialog, dialogData, error, importType } = this.state;
    let importing = {};
    let manage = '';
    if (importType === AdminGameActions.DATABASE_IMPORT) {
      importing = databaseImporting;
    } else if (importType === AdminGameActions.GAME_IMPORT) {
      importing = gameImporting;
    }
    if (user.groups.admin === true) {
      manage = (
        <React.Fragment>
          <Link className="btn btn-lg btn-primary mb-4"
            to={reverse(`${routes.listUsers}`)}>Modify Users
          </Link>
          <Link className="btn btn-lg btn-primary mb-5"
            to={reverse(`${routes.guestLinks}`)}>Guest links
          </Link>
          <button className="btn btn-lg btn-primary mb-4"
            onClick={this.onClickImportGame}>Import Game
          </button>
          <button className="btn btn-lg btn-primary mb-4"
            onClick={this.onClickImportDatabase}>Import Database
          </button>
          <button className="btn btn-lg btn-primary mb-5"
            onClick={this.exportDatabase}>Export Database
          </button>
        </React.Fragment>
      );
    }

    return (
      <div id="user-page">
        {error && <div className="alert alert-warning"
          role="alert"><span className="error-message">{error}</span></div>}
        <div className="user-details border border-secondary rounded">
          <div className="form-group row">
            <label htmlFor="username" className="col-sm-2 col-form-label field">Username</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext value" id="username">
                {user.username}
              </div>
            </div>
          </div>
          <div className="form-group row">
            <label htmlFor="email" className="col-sm-2 col-form-label">Email</label>
            <div className="col-sm-10">
              <div className="form-control-plaintext" id="email">
                {user.email}
              </div>
            </div>
          </div>
        </div>
        <div className="user-commands">
          {manage}
          {user.guest.loggedIn !== true && <Link to={reverse(`${routes.changeUser}`)}
            className="btn btn-lg btn-warning change-user mt-3 mb-5">
            Change password or email address</Link>}
          <Link to={reverse(`${routes.logout}`)}
            className="btn btn-lg btn-primary logout mb-5">Log out</Link>
        </div>
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} {...importing} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
    databaseImporting: getDatabaseImportState(state),
    gameImporting: getGameImportState(state),
  };
};

UserPage = connect(mapStateToProps)(UserPage);

export { UserPage };
