import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Table, Column, HeaderCell } from 'rsuite-table';
import { isEqual } from 'lodash';

import 'rsuite-table/dist/css/rsuite-table.css';

import { ConfirmDialog } from '../../components';
import { LoginDialog } from '../../user/components/LoginDialog';
import { AddUserDialog } from './AddUserDialog';
import {
  BoolCell,
  EditableTextCell,
  SelectCell,
  TextCell
} from '../../components';

import { fetchUserIfNeeded } from '../../user/userSlice';
import {
  AvailableGroups, fetchUsersIfNeeded, invalidateUsers,
  modifyUser, bulkModifyUsers, saveModifiedUsers,
  addUser
} from '../adminSlice';

import { getUser } from '../../user/userSelectors';
import { getUsersList } from '../adminSelectors';

import '../styles/admin.scss';

function rowClassName(rowData) {
  if (rowData === undefined) {
    return "";
  }
  const classNames = [];
  if (rowData.modified === true) {
      classNames.push('modified');
  }
  if (rowData.deleted === true) {
      classNames.push('deleted');
  }
  return classNames.join(' ');
}

class UsersListPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: PropTypes.object.isRequired,
    users: PropTypes.array.isRequired,
  };

  constructor(props) {
    super(props);
    let { users } = props;
    if (users === undefined) {
      users = [];
    }

    this.state = {
      ActiveDialog: null,
      dialogData: null,
      defaultSorted: [{
        dataField: 'id',
        order: 'asc'
      }],
      selectRowProps: {
        mode: 'checkbox',
        hideSelectAll: true,
        clickToSelect: false,
        onSelect: this.onSelectOne
      },
      sortColumn: "username",
      sortType: "desc",
      allSelected: false,
      data: users
    };
  }

  componentDidMount() {
    const { dispatch, users } = this.props;

    dispatch(fetchUserIfNeeded());
    this.checkUserStatus();
    if (users) {
      const { sortColumn, sortType } = this.state;
      const data = this.sortData({
        data: users,
        sortColumn,
        sortType
      });
      this.setState({ data, selections: {} });
    }
  }

  componentDidUpdate(prevProps) {
    const { user, users } = this.props;
    if (!isEqual(user, prevProps.user) && !user.isFetching) {
      this.checkUserStatus();
    }
    if (!isEqual(prevProps.users, users)) {
      const { sortColumn, sortType } = this.state;
      const data = this.sortData({
        data: users,
        sortColumn,
        sortType
      });
      this.setState({ data, selections: {} });
    }
  }

  checkUserStatus() {
    const { dispatch, user } = this.props;
    if (user.loggedIn) {
      const { ActiveDialog } = this.state;
      dispatch(fetchUsersIfNeeded());
      if (ActiveDialog === LoginDialog) {
        this.setState({ ActiveDialog: null, dialogData: null });
      }
    } else {
      this.setState({
        ActiveDialog: LoginDialog,
        dialogData: {
          dispatch,
          user,
          onCancel: this.cancelDialog,
          onSuccess: this.cancelDialog,
        }
      });
    }
  }

  /* onEnableEditCell = ({ dataKey, rowData }) => {
    const data = this.state.data.map(item => {
      if (item.pk === rowData.pk) {
        return {
          ...item,
          editing: {
            dataKey,
            value: item[dataKey]
          }
        };
      }
      if (typeof (item.editing) === "object") {
        return {
          ...item,
          [item.editing.dataKey]: item.editing.value,
          editing: null
        }
      }
      return item;
    });
    this.setState({ data });
  };*/

  onChangeCell = ({ rowData, dataKey, value }) => {
    let modified = false;
    const data = this.state.data.map(item => {
      if (item.pk !== rowData.pk || item[dataKey] === value) {
        return item;
      }
      modified = true;
      return {
        ...item,
        [dataKey]: value,
        modified
      };
    });
    if (modified) {
      this.setState({ data });
      const { dispatch } = this.props;
      //console.log(oldValue, newValue, row, column);
      dispatch(modifyUser({ pk: rowData.pk, field: dataKey, value }));
    }
  };

  onClickGroupCell = ({ user, group, value }) => {
    const { dispatch } = this.props;
    const groups = {
      ...user.groups,
      [group]: !value,
    };
    this.setState((state, props) => {
      const data = state.data.map((item) => {
        if (item.pk === user.pk) {
          return {
            ...item,
            groups
          };
        }
        return item;
      });
      return ({ data });
    }, () => dispatch(modifyUser({ pk: user.pk, field: 'groups', value: groups })));
  }

  sortData({ data, sortColumn, sortType }) {
    const result = [ ...data ];
    result.sort((a, b) => {
      if (a[sortColumn] < b[sortColumn]) {
        return (sortType === "desc") ? -1 : 1;
      }
      if (a[sortColumn] > b[sortColumn]) {
        return (sortType === "desc") ? 1 : -1;
      }
      return 0;
    });
    return result;
  }

  onClickSelect = ({ rowData, checked }) => {
    const data = this.state.data.map(item => {
      if (item.pk !== rowData.pk) {
        return item;
      }
      return {
        ...item,
        selected: checked
      };
    });
    let allSelected = checked;
    if (checked) {
      data.forEach(item => {
        allSelected = allSelected && (item.selected === true);
      });
    }
    this.setState({ allSelected, data });
  };

  onSelectAllChange = (ev) => {
    const allSelected = ev.target.checked;
    const data = this.state.data.map(item => ({
      ...item,
      selected: allSelected
    }));
    this.setState({ allSelected, data});
  };

  /*  editUserCell = (row) => (
    <button type="button" className="btn btn-primary" onClick={(ev) => this.onClickEdit(ev, row)}>
      Edit
    </button>
  );

onClickEdit = (ev, row) => {
  ev.preventDefault();
  console.dir(row);
}; */

  onSortColumn = (sortColumn, sortType) => {
    const data = this.sortData({ data: this.state.data, sortColumn, sortType });
    this.setState({
      sortColumn,
      sortType,
      data
    });
  };

  addUser = () => {
    const { users } = this.props;

    this.setState({
      ActiveDialog: AddUserDialog,
      dialogData: {
        onAddUser: this.confirmAddUser,
        onClose: this.cancelDialog,
        backdrop: true,
        users
      }
    });
  }

  confirmAddUser = (user) => {
    const { dispatch } = this.props;
    this.setState({
      ActiveDialog: null,
      dialogData: null
    });
    dispatch(addUser(user));
    return Promise.resolve(true);
  };

  deleteUsers = () => {
    const { dispatch } = this.props;
    const { data } = this.state;
    const selected = data.filter((user) => user.selected).map((user) => user.pk);
    dispatch(bulkModifyUsers({ users: selected, field: 'deleted', value:true }));
  }

  undeleteUsers = () => {
    const { dispatch } = this.props;
    const { data } = this.state;
    const selected = data.filter((user) => user.selected).map((user) => user.pk);
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
      if (user.newUser === true) {
        changes.push(`Add ${user.username} <${user.email}>`);
      } else if (user.deleted === true) {
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
    const { user } = this.props;
    const { allSelected, ActiveDialog, dialogData, data, sortColumn, sortType } = this.state;
    return (
      <div id="list-users-page" className={(ActiveDialog || !user.loggedIn) ? 'modal-open' : ''}  >
        <div className="action-panel" role="group">
          <button type="button" className="btn btn-success" onClick={this.addUser}>Add</button>
          <button type="button" className="btn btn-danger" onClick={this.deleteUsers}>Delete</button>
          <button type="button" className="btn btn-success" onClick={this.undeleteUsers}>Undelete</button>
          <button type="button" className="btn btn-success" onClick={this.askSaveChanges}>Save Changes</button>
          <button type="button" className="btn btn-primary" onClick={this.reloadUsers}>Reload</button>
        </div>
        <Table
          title="Users"
          rowKey='pk'
          autoHeight
          bordered
          cellBordered
          data={data}
          sortColumn={sortColumn}
          sortType={sortType}
          onSortColumn={this.onSortColumn}
          rowClassName={rowClassName}
          width={40 + 55 + 225 + 375 + 75 * AvailableGroups.length}
        >
          <Column width={40} align="center" fixed>
            <HeaderCell>
              <input type="checkbox" name="sel-all" onChange={this.onSelectAllChange} checked={allSelected} />
            </HeaderCell>
            <SelectCell dataKey="selected" onClick={this.onClickSelect} className={rowClassName} />
          </Column>
          <Column width={55} align="right" sortable fixed resizable>
            <HeaderCell>ID</HeaderCell>
            <TextCell dataKey="pk" className={rowClassName}/>
          </Column>
          <Column width={225} align="left" sortable fixed resizable>
            <HeaderCell>Username</HeaderCell>
            <EditableTextCell onChange={this.onChangeCell} dataKey="username" className={rowClassName}/>
          </Column>
          <Column width={375} align="left" sortable fixed resizable>
            <HeaderCell>Email</HeaderCell>
            <EditableTextCell dataKey="email" onChange={this.onChangeCell} className={rowClassName} />
          </Column>
          {AvailableGroups.map((name, idx) => (
            <Column width={75} align="center" key={idx}>
              <HeaderCell>{name}</HeaderCell>
              <BoolCell group={name} onClick={this.onClickGroupCell} className={rowClassName} />
            </Column>
          ))}
        </Table>
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  return {
    users: getUsersList(state, props),
    user: getUser(state, props),
  };
};

UsersListPage = connect(mapStateToProps)(UsersListPage);

export {
  UsersListPage
};
