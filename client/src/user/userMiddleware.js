import { LOCATION_CHANGE } from 'connected-react-router';

import { setActiveGame } from './userSlice';

const usersMiddleware = store => next => action => {
  if (action.type !== LOCATION_CHANGE) {
    return next(action);
  }
  const { dispatch, getState } = store;
  const state = getState();
  let { pathname } = state.router.location;
  let { activeGame } = state.user;
  pathname = pathname.split('/');
  if (!pathname) {
    pathname = ['', 'home'];
  }
  if (pathname.length < 3) {
    activeGame = 0;
  } else if (!/user/.test(pathname[1])) {
    activeGame = parseInt(pathname[2]);
  }
  if (!isNaN(activeGame) && activeGame !== state.user.activeGame) {
    dispatch(setActiveGame(activeGame));
  }
  return next(action);
};

export default usersMiddleware;