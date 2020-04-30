import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import BootstrapTable from 'react-bootstrap-table-next';
import cellEditFactory from 'react-bootstrap-table2-editor';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import { AvailableGroups, fetchUsersIfNeeded } from '../adminSlice';
import { LoginDialog } from '../../user/components/LoginDialog';

import '../styles/admin.scss';

const BoolIcon = ({ user, group }) => {
  if (user.groups[group] === true) {
    return <span className="bool-cell group-true">&#x2714;</span>;
  }
  return <span className="bool-cell group-false">&#x2718;</span>;
};

export const BoolCell = (cell, row, rowIdx, formatExtraData) => {
  if (cell === true) {
    return <span className="bool-cell group-true">&#x2714;</span>;
  }
  return <span className="bool-cell group-false">&#x2718;</span>;
};


const TableRow = ({ user }) => {
  return (
    <tr>
      <td className="pk-column">{user.pk}</td>
      <td className="username-column">{user.username}</td>
      <td className="email-column">{user.email}</td>
      {AvailableGroups.map((name, idx) => <td key={idx} className={`group-column group-${name}`}>
          <BoolIcon user={user} group={name} />
        </td>)}
    </tr>
  );
};

class UsersListPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    loggedIn: PropTypes.bool.isRequired,
    user: PropTypes.object.isRequired,
    users: PropTypes.array.isRequired,
  };

  constructor(props) {
    super(props);

    const groupColumns = AvailableGroups.map(name => ({
      dataField: `groups.${name}`,
      text: name,
      align: 'center',
      classes: `group-column group-${name}`,
      headerClasses: `group-column group-${name}`,
      formatter: BoolCell,
    }));

    this.state = {
      columns: [
        {
          dataField: 'pk',
          text: '#',
          sort: true,
          align: 'right',
          classes: 'pk-column',
          headerClasses: 'pk-column',
          sort: true,
        }, {
          dataField: 'username',
          text: 'Username',
          sort: true,
          filter: textFilter(),
          editable: true,
          classes: 'username-column',
          headerClasses: 'username-column',
          sort: true,
        }, {
          dataField: 'email',
          text: 'Email',
          sort: true,
          filter: textFilter(),
          editable: true,
          classes: 'email-column',
          headerClasses: 'email-column',
          sort: true,
        },
        ...groupColumns,
      ],
      cellEdit: cellEditFactory({
        mode: 'click',
        blurToSave: true,
        afterSaveCell: this.onChangeCell
      }),
      defaultSorted: [{
        dataField: 'id',
        order: 'asc'
      }],
      selectRowProps: {
        mode: 'checkbox',
        clickToSelect: false,
        onSelect: this.onSelectOne,
        onSelectAll: this.onSelectAll,
      },
    };
  }

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchUsersIfNeeded());
  }

  onTableMount = (table) => {
    this.table = table;
  }

  render() {
    const { users, loggedIn } = this.props;
    const { cellEdit, columns, defaultSorted, selectRowProps } = this.state;
    return (
      <div id="list-users-page" className={loggedIn ? '' : 'modal-open'}  >
        <BootstrapTable
          keyField='pk'
          cellEdit={cellEdit}
          columns={columns}
          classes="user-list"
          data={users}
          defaultSorted={defaultSorted}
          filter={filterFactory()}
          selectRow={selectRowProps}
          ref={this.onTableMount}
          striped
          bootstrap4
        />



        <table className="table table-striped table-bordered user-list">
          <thead>
            <tr>
              <th colSpan="3"></th>
              <th className="groups-column" colSpan={AvailableGroups.length} > Groups</th>
            </tr>
            <tr>
              <th className="pk-column">#</th>
              <th className="username-column">Username</th>
              <th className="email-column">Email</th>
              {AvailableGroups.map((name, idx) => <th key={idx} className={`group-column group-${name}`}>{name}</th>)}
              </tr>
          </thead>
          <tbody>
            {users.map((user, idx) => (<TableRow user={user} key={idx} />))}
          </tbody>
        </table>

        {!loggedIn && <LoginDialog backdrop dispatch={this.props.dispatch} onSuccess={() => null} />}
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, admin } = state;
  return {
    loggedIn: userIsLoggedIn(state),
    users: admin.users,
    user,
  };
};

UsersListPage = connect(mapStateToProps)(UsersListPage);

export {
  UsersListPage
};
