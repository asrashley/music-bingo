import { createSelector } from 'reselect';

import { ImportInitialFields } from './adminSlice';

const getUser = (state) => state.user;
const _getAdminUserPk = (state) => state.admin.user;
const _getUsers = (state) => state.admin.users;
const _getGuest = (state) => state.admin.guest;
const getLastUpdated = (state) => state.admin.lastUpdated;

export const getUsersList = createSelector([_getUsers, getLastUpdated],
  (users, lastUpdated) => {
    const retval = users.map(user => ({
      ...user,
      selected: false
    }));
    retval.lastUpdated = lastUpdated;
    return retval;
  });

export const getUsersMap = createSelector(
  [getUser, _getUsers], (user, users) => {
    const usersMap = {};
    if (user.groups.admin === true || user.groups.hosts === true) {
      users.forEach(u => usersMap[u.pk] = u);
    }
    return usersMap;
  });

export const getGuestTokens = createSelector(
  [_getGuest], (guest) => guest.tokens
);

export const getGuestLastUpdated = createSelector(
  [_getGuest], (guest) => guest.lastUpdated
);

export const getAdminUserPk = createSelector(
  [_getAdminUserPk], (pk) => pk
);

const _getImportState = (state) => state.admin.importing;

export const getDatabaseImportState = createSelector(
  [_getImportState], (impState) => {
    if (impState === null) {
      return {
        ...ImportInitialFields,
        added: [],
        importing: ''
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
      added,
      importing: 'database'
    };
  });
