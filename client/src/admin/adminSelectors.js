import { createSelector } from 'reselect';

import { ImportInitialFields } from './adminSlice';

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

const importState = (state) => state.admin.importing;

export const getDatabaseImportState = createSelector(
  [importState], (impState) => {
    if (impState === null) {
      return {
        ...ImportInitialFields,
        added: [],
      };
    }
    const added = [];
    if (impState.added) {
      for (let table in impState.added) {
        let name;
        if (/Directory/.test(table)) {
          name = 'Directories';
        } else {
          name = `${table}s`;
        }
        added.push({
          name,
          count: impState.added[table]
        });
      }
    }
    return {
      ...impState,
      added
    };
  });
