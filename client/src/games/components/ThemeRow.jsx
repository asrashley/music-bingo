import React from 'react';
import PropTypes from 'prop-types';

import { colours } from './colourPalette';
import { ThemePropType } from '../types/Theme';

export function ThemeRow({ index, theme }) {
  const style = {
    width: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  return (
    <tr className="theme">
      <td className="title" style={{ color: colours[index % colours.length] }}>{theme.title}</td>
      <td className="count"><div className="bar" style={style}>{theme.count}</div> </td>
    </tr>
  );
}
ThemeRow.propType = {
  index: PropTypes.number.isRequired,
  theme: ThemePropType.isRequired
};