import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { fetchDirectoriesIfNeeded, fetchDirectoryDetailIfNeeded, toggleDirectoryExpand } from '../directoriesSlice';
import { fetchUserIfNeeded } from '../../user/userSlice';

import { getDirectoryList, getSortOptions, getLastUpdated } from '../directoriesSelectors';
import { getUser } from '../../user/userSelectors';

import { initialState } from '../../app/initialState';

import '../styles/directories.scss';

const SongRow = ({ onSelect, song, selected }) => {
  let className = "song";
  if (selected.song?.pk === song.pk) {
    className += ' is-selected';
  }
  return (
    <li className={className}>
      <button className="btn btn-link song-link" onClick={(ev) => { ev.preventDefault(); onSelect({ song }); }} > {song.title}</button>
    </li>
  );
};

SongRow.propTypes = {
  song: PropTypes.object.isRequired
};

const SongListing = ({ songs, onSelect, selected }) => {
  return (
    <ul className="song-listing">
      {songs.map((song, idx) => (<SongRow song={song} onSelect={onSelect}
        key={idx} selected={selected} />))}
    </ul>
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
    const prefix = directory.expanded ? '-' : '+';
    return (<button className={`${className} btn btn-link directory-link`} onClick={(ev) => onVisibilityToggle(directory)}>
      {prefix}&nbsp;{directory.title}</button>);
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

const DirectoryChildren = ({ directory, options, onSelect, onVisibilityToggle, selected }) => {
  let collapse = 'collapse';
  if (directory.expanded) {
    collapse += ' show';
  }
  return (
    <div className={collapse}>
      {
        directory.directories.length > 0 && <DirectoryListing options={options}
          directories={directory.directories} onSelect={onSelect}
          onVisibilityToggle={onVisibilityToggle} selected={selected} />
      }
      {
        (directory.songs.length > 0 && directory.valid === true) && <SongListing options={options}
          songs={directory.songs} onSelect={onSelect} selected={selected} />
      }
    </div>
  );
};

const DirectoryRow = ({ options, directory, onSelect, onVisibilityToggle, selected }) => {
  const expandable = directory.directories.length > 0 || directory.songs.length > 0;
  const titleClass = selected.directory?.pk === directory.pk ? 'title is-selected' : 'title';
  let className = 'directory';
  if (directory.expanded) {
    className += ' expanded';
  } else if (expandable) {
    className += ' expandable';
  }
  return (
    <li className={className}>
      <TitleCell
        className={titleClass}
        directory={directory}
        onSelect={onSelect}
        onVisibilityToggle={onVisibilityToggle}
      />
      {
        expandable && <DirectoryChildren
          directory={directory}
          options={options}
          onSelect={onSelect}
          onVisibilityToggle={onVisibilityToggle}
          selected={selected}
        />
      }
    </li>
  );
};

const DirectoryListing = ({ directories, options, onSelect, onVisibilityToggle, selected }) => {
  return (
    <div className="directory-listing">
      <ul>
        {
          directories.map((dir, idx) => (
            <DirectoryRow
              directory={dir}
              options={options}
              key={idx}
              onSelect={onSelect}
              onVisibilityToggle={onVisibilityToggle}
              selected={selected}
            />))
        }
      </ul>
    </div>
  );
};

function DetailsPanel({ className, selected }) {
  let rows = [];
  const { directory, song } = selected;
  if (directory === null && song === null) {
    return (<div className={className} />);
  }

  if (song !== null) {
    rows = Object.keys(song).map(field => ({ field, value: song[field] }));
  } else if (directory !== null) {
    rows = [
      {
        field: 'title',
        value: directory.title
      },
      {
        field: 'pk',
        value: directory.pk
      },
      {
        field: 'name',
        value: directory.name
      },
      {
        field: 'parent',
        value: directory.parent
      },
      {
        field: 'children',
        value: `${directory.directories.length} directories`
      },
      {
        field: 'songs',
        value: `${directory.songs.length} songs`
      },
    ];
  }

  return (
    <div className={className}>
      <table className="table table-striped table-bordered">
        <thead>
          <tr><th>Field</th><th>Value</th></tr>
        </thead>
        <tbody>
          {
            rows.map((item, key) => (
              <tr key={key}>
                <td className="field">{item.field}</td>
                <td className="value">{item.value}</td>
              </tr>
            ))
          }
          </tbody>
        </table>
    </div>
  );
}

class DirectoryListPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ActiveDialog: null,
      dialogData: null,
      selected: {
        directory: null,
        song: null
      },
    };
  }

  componentDidMount() {
    const { dispatch, user } = this.props;
    dispatch(fetchUserIfNeeded());
    if (user.pk > 0) {
      dispatch(fetchDirectoriesIfNeeded());
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user } = this.props;
    if (prevProps.user.pk !== user.pk && user.pk > 0) {
      dispatch(fetchDirectoriesIfNeeded());
    }
  }

  onVisibilityToggle = (directory) => {
    const { pk, expanded } = directory;
    const { dispatch } = this.props;
    /*console.log(`${expanded} ${pk}`);*/
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

  render() {
    const { directories, options, user } = this.props;
    const { ActiveDialog, dialogData, selected } = this.state;

    return (
      <div id="directories-page" className={user.loggedIn ? '' : 'modal-open'}  >
        <DirectoryListing className="directory-listing"
          directories={directories}
          options={options}
          onSelect={this.onSelect}
          onVisibilityToggle={this.onVisibilityToggle}
          selected={selected}
        />
        <DetailsPanel className="directory-detail" selected={selected} />
        {ActiveDialog && <ActiveDialog backdrop {...dialogData} />}
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    directories: getDirectoryList(state, ownProps),
    options: getSortOptions(state, ownProps),
    lastUpdated: getLastUpdated(state, ownProps),
    user: getUser(state, ownProps),
  };
};

DirectoryListPage = connect(mapStateToProps)(DirectoryListPage);

export { DirectoryListPage };
