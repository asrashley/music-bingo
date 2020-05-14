import { createSelector } from 'reselect';

const _getUser = (state) => state.user;

export const getUser = createSelector([_getUser], (user) => {
  return {
    ...user,
    loggedIn: (user.pk > 0 && user.error === null && user.isFetching === false)
  }
});

export const userIsLoggedIn = createSelector([_getUser],
  (user) => (user.pk > 0 && user.error === null && user.isFetching === false));

