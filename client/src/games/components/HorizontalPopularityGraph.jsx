import React from 'react';
import PropTypes from 'prop-types';

import { ThemeRow } from './ThemeRow';
import { ThemePropType } from '../types/Theme';

export function HorizontalPopularityGraph({ popularity, onRotate }) {
  return (
    <table className="horiz-popularity-graph">
      <thead>
        <tr>
          <th className="title">Theme</th>
          <th className="count">Popularity
            <button className="btn btn-light rotate-icon" onClick={onRotate}>&nbsp;</button>
          </th>
        </tr>
      </thead>
      <tbody>
        {popularity.map((theme, idx) => <ThemeRow key={idx} index={idx} theme={theme} />)}
      </tbody>
    </table>
  );
}

HorizontalPopularityGraph.propTypes = {
  popularity: PropTypes.arrayOf(ThemePropType).isRequired,
  onRotate: PropTypes.func.isRequired
};
