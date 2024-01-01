import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { DetailsPanel } from './DetailsPanel';
import { DirectoryListing } from './DirectoryListing';
import { SearchResults } from './SearchResults';

import {
  clearSeachResults,
  fetchDirectoriesIfNeeded,
  fetchDirectoryDetailIfNeeded,
  toggleDirectoryExpand,
  searchForSongs
} from '../directoriesSlice';

import { fetchUserIfNeeded } from '../../user/userSlice';

import {
  getDirectoryList,
  getDirectoryMap,
  getSortOptions,
  getLastUpdated,
  getDirPk,
  getSearchResults,
  getSearchText,
  getIsSearching
} from '../directoriesSelectors';

import { getUser } from '../../user/userSelectors';
import { UserPropType } from '../../user/types/User';
import { DirectoryPropType } from '../types/Directory';

import '../styles/directories.scss';

class DirectoryListPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    directories: PropTypes.arrayOf(DirectoryPropType).isRequired,
    directoryMap: PropTypes.object.isRequired,
    isSearching: PropTypes.bool,
    options: PropTypes.object.isRequired,
    lastUpdated: PropTypes.number,
    location: PropTypes.number,
    queryResults: PropTypes.array,
    searchText: PropTypes.string,
    user: UserPropType.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      query: "",
      selected: {
        directory: null,
        song: null
      }
    };
    this.timeout = null;
  }

  componentDidMount() {
    const { directoryMap, dispatch, location, user } = this.props;
    dispatch(clearSeachResults());
    dispatch(fetchUserIfNeeded());
    if (user.pk > 0) {
      dispatch(fetchDirectoriesIfNeeded());
      if (location !== undefined) {
        if (directoryMap[location]?.expanded === false) {
          dispatch(fetchDirectoryDetailIfNeeded(location));
          dispatch(toggleDirectoryExpand({ dirPk: location }));
        }
      }
    }
  }

  componentDidUpdate(prevProps) {
    const { directoryMap, dispatch, location, user } = this.props;
    if (prevProps.user.pk !== user.pk && user.pk > 0) {
      dispatch(fetchDirectoriesIfNeeded());
      if (location !== undefined) {
        if (directoryMap[location]?.expanded === false) {
          dispatch(fetchDirectoryDetailIfNeeded(location));
          dispatch(toggleDirectoryExpand({ dirPk: location }));
        }
      }
    }
    if (user.pk > 0 && location !== undefined &&
      prevProps.directories.length !== this.props.directories.length) {
      if (directoryMap[location]?.expanded === false) {
        dispatch(fetchDirectoryDetailIfNeeded(location));
        dispatch(toggleDirectoryExpand({ dirPk: location }));
      }
    }
  }

  componentWillUnmount() {
    this.clearTimeout();
  }

  clearTimeout = () => {
    if (this.timeout !== null) {
      window.clearTimeout(this.timeout);
      this.timeout = null;
    }
  };

  onVisibilityToggle = (directory) => {
    const { pk, expanded } = directory;
    const { dispatch } = this.props;
    if (!expanded) {
      dispatch(fetchDirectoryDetailIfNeeded(pk));
    }
    dispatch(toggleDirectoryExpand({ dirPk: pk }));
    this.setState({ selected: { directory, song: null } });
  };

  onSelect = ({ directory, song }) => {
    if (directory === undefined) {
      directory = null;
    }
    if (song === undefined) {
      song = null;
    }
    this.setState({ selected: { directory, song } });
  };

  onChangeQuery = (event) => {
    const { location, searchText } = this.props;
    const minLength = location ? 1 : 3;
    const timeout = location ? 100 : 250;
    event.preventDefault();
    this.clearTimeout();
    this.setState({ query: event.target.value });
    if (event.target.value.length >= minLength ||
      (searchText !== '' && searchText !== event.target.value)) {
      this.timeout = setTimeout(this.makeQuery, timeout);
    }
  };

  makeQuery = () => {
    const { dispatch, isSearching, location } = this.props;
    const { query } = this.state;
    const minLength = location ? 1 : 3;
    if (isSearching === true) {
      this.clearTimeout();
      this.timeout = setTimeout(this.makeQuery, 100);
      return;
    }
    this.setState({
      selected: {
        directory: null,
        song: null
      }
    });
    if (query.length < minLength) {
      dispatch(clearSeachResults());
    } else {
      dispatch(searchForSongs(query, location));
    }
  };

  render() {
    const { directories, directoryMap, location, options, user, queryResults } = this.props;
    const { selected, query } = this.state;
    let column1;

    if (location === undefined && queryResults.length > 0) {
      column1 = <SearchResults
        options={options}
        onSelect={this.onSelect}
        queryResults={queryResults}
        selected={selected} />;
    } else {
      column1 = <table className="directory-listing table table-sm table-bordered table-hover">
        <thead className="thead-light">
          <tr>
            <th className="select"></th>
            <th className="title">Title</th>
            <th className="artist">Artist</th>
          </tr>
        </thead>
        <tbody>
          <DirectoryListing
            className="directory-listing"
            depth={0}
            directories={directories}
            options={options}
            onSelect={this.onSelect}
            onVisibilityToggle={this.onVisibilityToggle}
            selected={selected}
          />
        </tbody>
      </table>;
    }
    return (
      <div id="directories-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <input
          name="query"
          placeholder="search..."
          type="text"
          className="song-search"
          value={query}
          onChange={this.onChangeQuery}
        />
        <div className="column1">{column1}</div>
        <DetailsPanel className="directory-detail" selected={selected} directoryMap={directoryMap} />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    directories: getDirectoryList(state, ownProps),
    directoryMap: getDirectoryMap(state, ownProps),
    isSearching: getIsSearching(state, ownProps),
    options: getSortOptions(state, ownProps),
    lastUpdated: getLastUpdated(state, ownProps),
    location: getDirPk(state, ownProps),
    queryResults: getSearchResults(state, ownProps),
    searchText: getSearchText(state, ownProps),
    user: getUser(state, ownProps),
  };
};

export const DirectoryListPage = connect(mapStateToProps)(DirectoryListPageComponent);
