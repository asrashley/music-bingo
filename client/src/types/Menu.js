import PropTypes from 'prop-types';

export const MenuItemPropType = PropTypes.shape({
    title: PropTypes.string.isRequired,
    href: PropTypes.string.isRequired,
});

export const SectionItemPropType = PropTypes.shape({
    active: PropTypes.bool,
    id: PropTypes.string.isRequired,
    item: PropTypes.string.isRequired,
    link: PropTypes.string.isRequired,
});
