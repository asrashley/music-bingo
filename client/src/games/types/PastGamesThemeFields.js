import PropTypes from 'prop-types';

export const PastGamesThemeFields = {
    elapsedTime: PropTypes.number.isRequired,
    key: PropTypes.string.isRequired,
    lastUsed: PropTypes.instanceOf(Date).isRequired,
    row: PropTypes.objectOf(PropTypes.number),
    title: PropTypes.string.isRequired,
};

export const PastGamesThemePropType = PropTypes.shape(PastGamesThemeFields);
