import React from 'react';
import PropTypes from 'prop-types';

import { DirectoryListing } from './DirectoryListing';
import { SongListing } from './SongListing';

export function DirectoryChildren({ depth, directory, options, onSelect, onVisibilityToggle, selected }) {
  return (
    <React.Fragment>
      {
        (directory.directories.length > 0) && <DirectoryListing
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
}

DirectoryChildren.propTypes = {
  depth: PropTypes.number.isRequired,
  directory: PropTypes.object.isRequired,
  options: PropTypes.object.isRequired,
  onSelect: PropTypes.func.isRequired,
  onVisibilityToggle: PropTypes.func.isRequired,
  selected: PropTypes.object.isRequired
};

