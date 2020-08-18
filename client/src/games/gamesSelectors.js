import { createSelector } from 'reselect';

import { gameInitialFields, ImportInitialFields } from './gamesSlice';

const getGames = (state) => state.games.games;
const getGameIds = (state) => state.games.gameIds;
export const getGameId = (state, props) => props.match ? props.match.params.gameId : null;
export const getPopularityOptions = (state) => state.games.popularity;

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
  [getPopularityOptions, getPastGamesList],
  (options, games) => {
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
    if (options && options.vertical) {
      keys.sort((a,b) => {
        if(a < b) {
          return 1;
        }
        if (b > a) {
          return -1;
        }
        return 0;
      });
    } else {
      keys.sort();
    }
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

const importState = (state) => state.games.importing;

export const getGameImportState = createSelector(
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
  }
);