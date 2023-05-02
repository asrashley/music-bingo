import React from 'react';
import PropTypes from 'prop-types';

import { ThemePropType } from '../types/Theme';

import { HorizontalPopularityGraph } from './HorizontalPopularityGraph';
import { VerticalPopularityGraph } from './VerticalPopularityGraph';

import '../styles/games.scss';

export function PopularityGraph({ popularity, toggleOrientation, options }) {
  if (options.vertical) {
    return <VerticalPopularityGraph popularity={popularity}
      onRotate={toggleOrientation} />;
  }
  return <HorizontalPopularityGraph popularity={popularity}
    onRotate={toggleOrientation} />;
}

PopularityGraph.propTypes = {
  popularity: PropTypes.arrayOf(ThemePropType).isRequired,
  toggleOrientation: PropTypes.func.isRequired,
  options: PropTypes.shape({
    vertical: PropTypes.bool
  }).isRequired
};
