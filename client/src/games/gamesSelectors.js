import { createSelector } from 'reselect';

const getGames = (state) => state.games.games;
export const getGamesOrder = (state) => state.games.order;
export const getPastGamesOrder = (state) => state.games.pastOrder;

function decorateGames(games, order) {
  let day = null;
  let round = 1;
  const retval = [];

  order.forEach(pk => {
    const game = games[pk];
    const start = new Date(game.start);
    if (start.getDay() !== day) {
      round = 1;
      day = start.getDay();
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

