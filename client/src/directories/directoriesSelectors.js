import { createSelector } from 'reselect';

const getDirectoryMap = (state) => state.directories.directories;

export const getSortOptions = (state) => state.directories.sortOptions;

export const getLastUpdated = (state) => state.directories.lastUpdated;

function getSong(song) {
  if (typeof(song) === "object") {
    return song;
  }
  return {
    title: `Song ${song}`,
    pk: song
  };
}

function getDirectory(pk, dirMap) {
  if (dirMap[pk] === undefined) {
    return undefined;
  }
  const valid = dirMap[pk].invalid === false &&
    (dirMap[pk].songs.length === 0 || dirMap[pk].lastUpdated !== null);
  const item = {
    ...dirMap[pk],
    directories: dirMap[pk].directories.map(pk => getDirectory(pk, dirMap)),
    songs: dirMap[pk].songs.map(song => getSong(song)),
    valid
  };
  return item;
}

export const getDirectoryList = createSelector(
  [getDirectoryMap, getSortOptions],
  (dirMap, options) => {
    const results = [];
    for (let pk in dirMap) {
      if (dirMap[pk].parent !== null) {
        continue;
      }
      const item = getDirectory(pk, dirMap);
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
