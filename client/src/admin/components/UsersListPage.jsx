import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import BootstrapTable from 'react-bootstrap-table-next';
import cellEditFactory from 'react-bootstrap-table2-editor';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';

import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import {
  AvailableGroups, fetchUsersIfNeeded, invalidateUsers,
  modifyUser, bulkModifyUsers, saveModifiedUsers
} from '../adminSlice';
import { LoginDialog } from '../../user/components/LoginDialog';
import { ConfirmDialog } from '../../components';

import '../styles/admin.scss';

export const BoolCell = (cell, row, rowIdx, formatExtraData) => {
  if (cell === true) {
    return <span className="bool-cell group-true">&#x2714;</span>;
  }
  return <span className="bool-cell group-false">&#x2718;</span>;
};

function rowClassName(name) {
  const callback = (cell, row, rowIndex, colIndex) => {
    const classNames = [
      `${name}-column`,
    ];
    if (row.modified === true) {
      classNames.push('modified');
    }
    if (row.deleted === true) {
      classNames.push('deleted');
    }
    return classNames.join(' ');
  };
  return callback;
}

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
      ActiveDialog: null,
      dialogData: null,
      columns: [
        {
          dataField: 'pk',
          text: '#',
          sort: true,
          align: 'right',
          classes: rowClassName('pk'),
          headerClasses: 'pk-column',
        }, {
          dataField: 'username',
          text: 'Username',
          sort: true,
          filter: textFilter(),
          editable: true,
          classes: rowClassName('username'),
          headerClasses: 'username-column',
        }, {
          dataField: 'email',
          text: 'Email',
          sort: true,
          filter: textFilter(),
          editable: true,
          classes: rowClassName('email'),
          headerClasses: 'email-column',
        }, {
          dataField: 'reset_date',
          text: 'Reset Request',
          sort: true,
          classes: rowClassName('reset'),
          headerClasses: 'reset-column',
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
        hideSelectAll: true,
        clickToSelect: false,
        onSelect: this.onSelectOne,
        selected: [],
        allSelected: false,
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

  onChangeCell = (oldValue, newValue, row, column) => {
    const { dispatch } = this.props;
    //console.log(oldValue, newValue, row, column);
    dispatch(modifyUser({ pk: row.pk, field: column.dataField, value: newValue }));
  }

  onSelectOne = ({ id, pk }, isSelected) => {
    const { selectRowProps } = this.state;
    let { selected } = selectRowProps;
    if (isSelected) {
      if (!(selected.includes(pk))) {
        selected = [...selected, pk];
        selected = selected.sort();
      }
    } else {
      selected = selected.filter((i) => {
        return i !== pk;
      });
    }
    this.setState({
      selectRowProps: {
        ...selectRowProps,
        selected,
        allSelected: false
      }
    });
    return false;
  }

  deleteUsers = () => {
    const { dispatch } = this.props;
    const { selectRowProps } = this.state;
    const { selected } = selectRowProps;
    dispatch(bulkModifyUsers({ users: selected, field: 'deleted', value:true }));
  }

  undeleteUsers = () => {
    const { dispatch } = this.props;
    const { selectRowProps } = this.state;
    const { selected } = selectRowProps;
    dispatch(bulkModifyUsers({ users: selected, field: 'deleted', value: false }));
  }

  reloadUsers = () => {
    const { dispatch } = this.props;
    dispatch(invalidateUsers());
    dispatch(fetchUsersIfNeeded());
  }

  askSaveChanges = () => {
    const { users } = this.props;
    const changes = [];
    users.forEach((user) => {
      if (user.deleted === true) {
        changes.push(`Delete ${user.username} <${user.email}>`);
      } else if (user.modified === true) {
        changes.push(`Modify ${user.username} <${user.email}>`);
      }
    });
    this.setState({
      ActiveDialog: ConfirmDialog,
      dialogData: {
        changes,
        title: "Confirm save changes",
        onCancel: this.cancelDialog,
        onConfirm: this.saveChanges,
      }
    });
  }

  cancelDialog = () => {
      this.setState({ ActiveDialog: null, dialogData: null });
  }

  saveChanges = () => {
    const { dispatch } = this.props;
    dispatch(saveModifiedUsers());
    this.setState({ ActiveDialog: null, dialogData: null })
  }

  render() {
    const { users, loggedIn } = this.props;
    const { ActiveDialog, dialogData, cellEdit, columns, defaultSorted, selectRowProps } = this.state;
    return (
      <div id="list-users-page" className={(ActiveDialog || !loggedIn) ? 'modal-open' : ''}  >
        <div className="action-panel border" role="group">
          <button type="button" className="btn btn-danger" onClick={this.deleteUsers}>Delete</button>
          <button type="button" className="btn btn-success" onClick={this.undeleteUsers}>Undelete</button>
          <button type="button" className="btn btn-success" onClick={this.askSaveChanges}>Save Changes</button>
          <button type="button" className="btn btn-primary" onClick={this.reloadUsers}>Reload</button>
        </div>
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
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
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
    users: admin.users.map(user => ({...user})),
    user,
  };
};

UsersListPage = connect(mapStateToProps)(UsersListPage);

export {
  UsersListPage
};
