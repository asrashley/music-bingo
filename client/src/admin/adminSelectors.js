import { createSelector } from 'reselect';

const getUser = (state) => state.user;
const _getUsers = (state) => state.admin.users;

export const getUsersList = createSelector([_getUsers],
  (users) => users.map(user => ({ ...user })));

export const getUsersMap = createSelector(
  [getUser, _getUsers], (user, users) => {
    const usersMap = {};
    if (user.groups.admin === true || user.groups.host === true) {
      users.forEach(u => usersMap[u.pk] = u);
    }
    return usersMap;
  });