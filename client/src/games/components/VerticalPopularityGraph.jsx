import React from 'react';
import PropTypes from 'prop-types';

import { colours } from './colourPalette';
import { ThemePropType } from '../types/Theme';

function Bar({ theme, index, scale }) {
  const barStyle = {
    height: `${100 * theme.count / theme.maxCount}%`,
    backgroundColor: colours[index % colours.length],
  };
  const nameStyle = {
    color: colours[index % colours.length],
  };
  const themeStyle = {
    fontSize: `${scale}em`
  };
  return (
    <div className="theme" style={themeStyle}>
      <div className="bar-wrap"><div className="bar" style={barStyle}>{theme.count}</div></div>
      <div className="name" style={nameStyle}>{theme.title}</div>
    </div>
  );
}
Bar.propTypes = {
  theme: ThemePropType.isRequired,
  index: PropTypes.number.isRequired,
  scale: PropTypes.number.isRequired
};

export function VerticalPopularityGraph({ popularity, onRotate }) {
  const scale = popularity.length > 30 ? (45 / popularity.length) : 1.0;
  return (
    <div className="vert-popularity-graph" data-testid="vert-popularity-graph">
      <button className="btn btn-light rotate-icon"
        data-testid="rotate-button"
        onClick={onRotate}>&nbsp;</button>
      {popularity.map((theme, idx) => <Bar
        key={theme.title}
        index={idx}
        theme={theme}
        scale={scale}
        length={popularity.length} />)}
    </div>
  );
}
VerticalPopularityGraph.propTypes = {
  popularity: PropTypes.arrayOf(ThemePropType).isRequired,
  onRotate: PropTypes.func.isRequired
};
