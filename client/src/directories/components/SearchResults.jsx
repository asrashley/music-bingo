import React from 'react';
import PropTypes from 'prop-types';

import { SongListing } from './SongListing';

export function SearchResults({ onSelect, options, queryResults, selected }) {
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
          depth={0}
          options={options}
          onSelect={onSelect}
          songs={queryResults}
          selected={selected} />
      </tbody>
    </table>
  );
}

SearchResults.propTypes = {
  onSelect: PropTypes.func.isRequired,
  options: PropTypes.object.isRequired,
  queryResults: PropTypes.array.isRequired,
  selected: PropTypes.object.isRequired
};
