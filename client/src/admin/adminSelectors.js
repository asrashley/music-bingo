import { createSelector } from 'reselect';

const getUser = (state) => state.user;
const _getAdminUserPk = (state) => state.admin.user;
const _getUsers = (state) => state.admin.users;
const _getGuest = (state) => state.admin.guest;

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

  export const getGuestTokens = createSelector(
    [_getGuest], (guest) => guest.tokens
  );

export const getAdminUserPk = createSelector(
  [_getAdminUserPk], (pk) => pk
);
