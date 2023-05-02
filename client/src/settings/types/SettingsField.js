import PropTypes from 'prop-types';

export const SettingsFieldPropType = PropTypes.shape({
  help: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  type: PropTypes.oneOf(["bool", "enum", "int", "json", "text"]).isRequired,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.bool,
    PropTypes.object
  ]),
  minValue: PropTypes.number,
  maxValue: PropTypes.number,
  choices: PropTypes.arrayOf(PropTypes.string)
});