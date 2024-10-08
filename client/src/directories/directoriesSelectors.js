import { createSelector } from 'reselect';
import { getRouteParams } from '../routes/routesSelectors';

export const getDirectoryMap = (state) => state.directories.directories;

export const getDisplayOptions = (state) => state.directories.displayOptions;

export const getLastUpdated = (state) => state.directories.lastUpdated;

export const getIsSearching = (state) => state.directories.query.isSearching;

const getSearchResultsPriv = (state) => state.directories.query.results;

const getSearchResultsMap = (state) => state.directories.query.resultMap;

export const getSearchText = (state) => state.directories.query.query;

export const getDirPk = createSelector([getRouteParams], (params = {}) => {
  let { dirPk } = params;
  if (dirPk !== undefined) {
    return parseInt(dirPk);
  }
  return dirPk;
});

function getSong(song, dirPk) {
  if (typeof (song) === "object") {
    return song;
  }
  return {
    title: `Song ${song}`,
    pk: song,
    directory: dirPk,
    duration: 0
  };
}

function getDirectory(pk, dirMap, searchResultsMap) {
  if (dirMap[pk] === undefined) {
    return undefined;
  }
  const valid = dirMap[pk].invalid === false &&
    (dirMap[pk].songs.length === 0 || dirMap[pk].lastUpdated !== null);
  let songs = dirMap[pk].songs.map(song => getSong(song, pk));
  if (searchResultsMap) {
    songs = songs.filter(song => song.pk in searchResultsMap);
  }

  const item = {
    ...dirMap[pk],
    directories: dirMap[pk].directories.map(pk => getDirectory(pk, dirMap)),
    songs,
    valid
  };
  return item;
}

export const getDirectoryList = createSelector(
  [getDirectoryMap, getDisplayOptions, getDirPk, getSearchResultsMap],
  (dirMap, options, location, searchResultsMap) => {
    const results = [];
    for (let pk in dirMap) {
      if (location === undefined) {
        if (dirMap[pk].parent !== null) {
          continue;
        }
      }
      else {
        if (dirMap[pk].pk !== location) {
          continue;
        }
      }
      const item = getDirectory(pk, dirMap, searchResultsMap);
      if (item !== undefined && (!options.onlyExisting || item.exists)) {
        results.push(item);
      }
    }
    results.sort((dirA, dirB) => {
      const a = dirA[options.field];
      const b = dirB[options.field];
      if (a < b) {
        return options.ascending ? -1 : 1;
      }
      if (b > a) {
        return options.ascending ? 1 : -1;
      }
      return 0;
    });
    return results;
  });

export const getSearchResults = createSelector(
  [getSearchResultsPriv],
  (searchResults) => searchResults.map(song => getSong(song)));
