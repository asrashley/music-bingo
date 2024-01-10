import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { directoriesSlice, DirectoryInitialState } from './directoriesSlice';
import * as user from '../../tests/fixtures/userState.json';

const directoryList = [{
  ...DirectoryInitialState(),
  "parent": null,
  "pk": 1,
  "name": "Clips",
  "title": "Clips",
  "directories": [2, 3, 4, 5, 6, 7],
  "songs": []
}];

describe('directoriesSlice', () => {
  it('records if fetching directories failed', () => {
    const store = createStore({
      ...initialState,
      directories: {
        ...initialState.directories,
        isFetching: true,
        error: null,
        lastUpdated: 1,
        invalid: false,
        user: user.pk,
      },
      user
    }, false);
    store.dispatch(directoriesSlice.actions.failedFetchDirectories({
      timestamp: 1234,
      error: 'an error message'
    }));
    const { isFetching, invalid, error, lastUpdated } = store.getState().directories;
    expect(isFetching).toEqual(false);
    expect(invalid).toEqual(true);
    expect(error).toEqual('an error message');
    expect(lastUpdated).toEqual(1234);
  });

  it('records if fetching directory details failed', () => {
    const initState = {
      ...initialState,
      directories: {
        ...initialState.directories,
        directories: {},
        isFetching: true,
        error: null,
        lastUpdated: 1,
        invalid: false,
        user: user.pk,
      },
      user
    };
    directoryList.forEach(directory => {
      initState.directories.directories[directory.pk] = directory;
    });
    const dirPk = directoryList[0].pk;
    initState.directories.directories[dirPk].isFetching = true;
    const store = createStore(initState, false);
    store.dispatch(directoriesSlice.actions.failedFetchDirectoryDetail({
      dirPk,
      timestamp: 1234,
      error: 'an error message'
    }));
    const { isFetching, invalid, error, lastUpdated } = store.getState().directories.directories[dirPk];
    expect(isFetching).toEqual(false);
    expect(invalid).toEqual(true);
    expect(error).toEqual('an error message');
    expect(lastUpdated).toEqual(1234);
  });

  it('records if searching for a song fails', () => {
    const query = 'Kylie';
    const store = createStore({
      ...initialState,
      directories: {
        ...initialState.directories,
        isFetching: true,
        error: null,
        lastUpdated: 1,
        invalid: false,
        user: user.pk,
        query: {
          dirPk: 12,
          searching: true,
          query,
        }
      },
      user
    }, false);
    store.dispatch(directoriesSlice.actions.failedSearchSongs({
      timestamp: 1234,
      error: 'an error message',
      dirPk: 12,
      query
    }));
    const { searching } = store.getState().directories.query;
    expect(searching).toEqual(false);
  });


});