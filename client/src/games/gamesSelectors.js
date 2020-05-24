import { createSelector } from 'reselect';

import { gameInitialFields } from './gamesSlice';

const getGames = (state) => state.games.games;
const getGameIds = (state) => state.games.gameIds;
export const getGameId = (state, props) => props.match ? props.match.params.gameId : null;

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
  (games, order) => decorateGames(games, order));

export const getPastGamesList = createSelector(
  [getGames, getPastGamesOrder],
  (games, order) => decorateGames(games, order));

export const getPastGamesPopularity = createSelector(
  [getPastGamesList],
  (games) => {
    const themes = {};
    let maxCount = 1;
    games.forEach(game => {
      const key = game.title.replace(/\W/g,'').toLowerCase();
      if (themes[key] === undefined) {
        themes[key] = {
          title: game.title,
          count: 1,
        };
      } else {
        themes[key].count++;
      }
      maxCount = Math.max(maxCount, themes[key].count);
    });
    const keys = Object.keys(themes);
    keys.sort();
    return keys.map(key => ({
      ...themes[key],
      maxCount,
    }));
  });

export const getGame = createSelector(
  [getGameId, getGames, getGameIds], (gameId, games, gameIds) => {
    const gamePk = gameIds[gameId];
    if (gamePk && games[gamePk]) {
      return games[gamePk];
    }
    return {
      ...gameInitialFields,
      placeholder: true,
    };
  });
