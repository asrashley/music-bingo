import React from 'react';
import PropTypes from 'prop-types';

import { DirectoryChildren } from './DirectoryChildren';
import { TitleCell } from './TitleCell';

export function DirectoryRow({ options, depth, directory, onSelect, onVisibilityToggle, selected }) {
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
      <tr className={className} id={`dir-${directory.pk}`}>
        <td className="select">
          <button
            className="btn btn-outline-dark btn-sm"
            data-testid={`dir-toggle-${directory.pk}`}
            onClick={() => onVisibilityToggle(directory)}
          >{prefix}</button>
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
}

DirectoryRow.propTypes = {
  options: PropTypes.object.isRequired,
  depth: PropTypes.number.isRequired,
  directory: PropTypes.object.isRequired,
  onSelect: PropTypes.func.isRequired,
  onVisibilityToggle: PropTypes.func.isRequired,
  selected: PropTypes.object.isRequired
};
