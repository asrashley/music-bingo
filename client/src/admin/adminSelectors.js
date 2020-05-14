import { createSelector } from 'reselect';

const _getUsers = (state) => state.admin.users;

export const getUsersList = createSelector([_getUsers],
  (users) => users.map(user => ({ ...user })));

