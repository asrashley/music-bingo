import React from 'react';
import PropTypes from 'prop-types';

export function TitleCell({ className, directory, onSelect, onVisibilityToggle }) {
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
  className: PropTypes.string,
  directory: PropTypes.object.isRequired,
  onSelect: PropTypes.func.isRequired,
  onVisibilityToggle: PropTypes.func.isRequired
};

