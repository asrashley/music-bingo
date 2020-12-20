import { createSelector } from 'reselect';

export const getDirectoryMap = (state) => state.directories.directories;

export const getSortOptions = (state) => state.directories.sortOptions;

export const getLastUpdated = (state) => state.directories.lastUpdated;

export const getIsSearching = (state) => state.directories.query.isSearching;

const getSearchResultsPriv = (state) => state.directories.query.results;

const getSearchResultsMap = (state) => state.directories.query.resultMap;

export const getSearchText = (state) => state.directories.query.query;

export const getLocation = (state, ownProps) => {
  let location = ownProps?.match?.params?.dirPk;
  if (location !== undefined) {
    location = parseInt(location);
  }
  return location;
};

function getSong(song) {
  if (typeof(song) === "object") {
    return song;
  }
  return {
    title: `Song ${song}`,
    pk: song
  };
}

function getDirectory(pk, dirMap, searchResultsMap) {
  if (dirMap[pk] === undefined) {
    return undefined;
  }
  const valid = dirMap[pk].invalid === false &&
    (dirMap[pk].songs.length === 0 || dirMap[pk].lastUpdated !== null);
  let songs = dirMap[pk].songs.map(song => getSong(song));
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
  [getDirectoryMap, getSortOptions, getLocation, getSearchResultsMap],
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
      if (item !== undefined) {
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
        return options.ascending ? 1: -1;
      }
      return 0;
    });
    return results;
  });

export const getSearchResults = createSelector(
  [getSearchResultsPriv],
  (searchResults) => searchResults.map(song => getSong(song)));
