import React from 'react';
import PropTypes from 'prop-types';

import { DirectoryRow } from './DirectoryRow';

export function DirectoryListing({ depth, directories, options, onSelect, onVisibilityToggle, selected }) {
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
}

DirectoryListing.propTypes = {
  options: PropTypes.object.isRequired,
  depth: PropTypes.number.isRequired,
  directories: PropTypes.array.isRequired,
  onSelect: PropTypes.func.isRequired,
  onVisibilityToggle: PropTypes.func.isRequired,
  selected: PropTypes.object.isRequired
};
