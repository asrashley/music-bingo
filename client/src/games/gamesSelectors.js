import { createSelector } from 'reselect';

const getGames = (state) => state.games.games;
export const getGamesOrder = (state) => state.games.order;
export const getPastGamesOrder = (state) => state.games.pastOrder;

function startOfDay(dateStr) {
  const rv = new Date(dateStr);
  rv.setHours(0);
  rv.setMinutes(0);
  rv.setSeconds(0);
  rv.setMilliseconds(0);
  return rv;
}

function decorateGames(games, order) {
  let day = null;
  let round = 1;
  const retval = [];

  order.forEach(pk => {
    const game = games[pk];
    const start = startOfDay(game.start).getTime();
    if (start !== day) {
      round = 1;
      day = start;
    } else {
      round += 1;
    }
    retval.push({ ...game, round });
  });
  return retval;
}

export const getActiveGamesList = createSelector(
  [getGames, getGamesOrder],
  (games, order) => decorateGames(games,order));

export const getPastGamesList = createSelector(
  [getGames, getPastGamesOrder],
  (games, order) => decorateGames(games, order));

