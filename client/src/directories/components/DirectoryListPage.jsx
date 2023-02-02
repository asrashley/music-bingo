import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { DetailsPanel } from './DetailsPanel';

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
  getLocation,
  getSearchResults,
  getSearchText,
  getIsSearching
} from '../directoriesSelectors';

import { getUser } from '../../user/userSelectors';

import '../styles/directories.scss';

const SongRow = ({ onSelect, depth, song, selected }) => {
  let className = "song";
  if (selected.song?.pk === song.pk) {
    className += ' is-selected';
  }
  return (
    <tr className={className}>
      <td className="select"></td>
      <td className="title" style={{ paddingLeft: `${depth}em` }}>
        <button className="btn btn-link song-link" onClick={(ev) => { ev.preventDefault(); onSelect({ song }); }} >
          {song.title}
        </button>
      </td>
      <td className="artist">
        {song.artist}
      </td>
    </tr>
  );
};

SongRow.propTypes = {
  song: PropTypes.object.isRequired
};

const SongListing = ({ depth, songs, onSelect, selected }) => {
  return (
    <React.Fragment>
      {songs.map((song, idx) => (<SongRow depth={depth} song={song} onSelect={onSelect}
        key={idx} selected={selected} />))}
    </React.Fragment>
  );
};

SongListing.propTypes = {
  options: PropTypes.object.isRequired,
  onSelect: PropTypes.func.isRequired,
  songs: PropTypes.array.isRequired,
  selected: PropTypes.object.isRequired
};

const TitleCell = ({ className, directory, onSelect, onVisibilityToggle }) => {
  if (directory.directories.length > 0 || directory.songs.length > 0) {
    return (<button className={`${className} btn btn-link directory-link`} onClick={(ev) => onVisibilityToggle(directory)}>
      {directory.title}</button>);
  }
  return (<button
    className={`${className} btn btn-link directory-link leaf`}
    onClick={(ev) => { ev.preventDefault(); onSelect({ directory }); }}
  >{directory.title}</button>);
};

TitleCell.propTypes = {
  options: PropTypes.object.isRequired,
  directory: PropTypes.object.isRequired,
  onVisibilityToggle: PropTypes.func.isRequired
};

const DirectoryChildren = ({ depth, directory, options, onSelect, onVisibilityToggle, selected }) => {
  return (
    <React.Fragment>
      {
        directory.directories.length > 0 && <DirectoryListing
          options={options}
          directories={directory.directories}
          depth={depth}
          onSelect={onSelect}
          onVisibilityToggle={onVisibilityToggle}
          selected={selected} />
      }
      {
        (directory.songs.length > 0 && directory.valid === true) && <SongListing options={options}
          depth={depth + 1} songs={directory.songs} onSelect={onSelect} selected={selected} />
      }
    </React.Fragment>
  );
};

const DirectoryRow = ({ options, depth, directory, onSelect, onVisibilityToggle, selected }) => {
  const expandable = directory.directories.length > 0 || directory.songs.length > 0;
  const titleClass = selected.directory?.pk === directory.pk ? 'title is-selected' : 'title';
  const prefix = directory.expanded ? '-' : '+';
  let className = 'directory';
  if (directory.expanded) {
    className += ' expanded';
  } else if (expandable) {
    className += ' expandable';
  }
  return (
    <React.Fragment>
      <tr className={className}>
        <td className="select">
          <button className="btn btn-outline-dark btn-sm" onClick={(ev) => onVisibilityToggle(directory)}>{prefix}</button>
        </td>
        <td className="directory" colSpan="2" style={{ paddingLeft: `${depth}em` }}>
          <TitleCell
            className={titleClass}
            directory={directory}
            onSelect={onSelect}
            options={options}
            onVisibilityToggle={onVisibilityToggle}
          />
        </td>
      </tr>
      {
        expandable && directory.expanded && <DirectoryChildren
          depth={depth + 1}
          directory={directory}
          options={options}
          onSelect={onSelect}
          onVisibilityToggle={onVisibilityToggle}
          selected={selected}
        />
      }
    </React.Fragment>
  );
};

const DirectoryListing = ({ depth, directories, options, onSelect, onVisibilityToggle, selected }) => {
  return <React.Fragment>
    {
      directories.map((dir, idx) => (
        <DirectoryRow
          depth={depth}
          directory={dir}
          options={options}
          key={idx}
          onSelect={onSelect}
          onVisibilityToggle={onVisibilityToggle}
          selected={selected}
        />))
    }
  </React.Fragment>;
};

function SearchResults({ onSelect, options, queryResults, selected }) {
  return (
    <table className="search-results table table-bordered table-sm table-hover">
      <caption>Search results</caption>
      <thead className="thead-light">
        <tr>
          <th className="select"></th>
          <th className="title">Title</th>
          <th className="artist">Artist</th>
        </tr>
      </thead>
      <tbody>
        <SongListing
          options={options}
          onSelect={onSelect}
          songs={queryResults}
          selected={selected} />
      </tbody>
    </table>
  );
}

class DirectoryListPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
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

  componentDidUpdate(prevProps, prevState) {
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
    const { ActiveDialog, dialogData, selected, query } = this.state;
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
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
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
    location: getLocation(state, ownProps),
    queryResults: getSearchResults(state, ownProps),
    searchText: getSearchText(state, ownProps),
    user: getUser(state, ownProps),
  };
};

DirectoryListPage = connect(mapStateToProps)(DirectoryListPage);

export { DirectoryListPage };
