import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { routes } from '../../routes/routes';

export function DetailsPanel({ className, selected, directoryMap }) {
  let rows = [];
  const { directory, song } = selected;
  if (directory === null && song === null) {
    return (<div className={className} />);
  }

  if (song !== null) {
    rows = Object.keys(song).map((field) => {
      const row = { field, value: song[field] };
      if (field === 'directory') {
        const subdir = directoryMap[row.value];
        const url = reverse(`${routes.listDirectory}`, { dirPk: subdir.pk });
        row.value = <Link to={url}>{subdir.title}</Link>;
      }
      return row;
    });
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
        value: directory.songs.length === 1 ? '1 song' : `${directory.songs.length} songs`
      },
    ];
  }

  return (
    <div className={className}>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th className="field">Field</th>
            <th className="value">Value</th>
          </tr>
        </thead>
        <tbody>
          {
            rows.map((item, key) => (
              <tr key={key}>
                <td className="field">{item.field}</td>
                <td className={`value ${item.field}-column`}>{item.value}</td>
              </tr>
            ))
          }
        </tbody>
      </table>
    </div>
  );
}

DetailsPanel.propTypes = {
  className: PropTypes.string,
  selected: PropTypes.object.isRequired,
  directoryMap: PropTypes.object.isRequired
};
