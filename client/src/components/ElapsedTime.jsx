import React from 'react';
import PropTypes from 'prop-types';

const unitMultipliers = [
    [3600 * 24 * 365.25, 'year'],
    [3600 * 24 * 7, 'week'],
    [3600 * 24, 'day'],
    [3600, 'hour'],
    [60, 'minute'],
];

export function elapsedTime(date) {
    const now = Date.now();
    const elapsed = (typeof (date) === 'number' ? date :
        (now - date.getTime())) / 1000;
    let value = elapsed;
    let units = 'second';
    for (let i = 0; i < unitMultipliers.length; ++i) {
        const [multiplier, name] = unitMultipliers[i];
        if (multiplier < elapsed) {
            value = Math.floor(elapsed / multiplier);
            units = name;
            break;
        }
    }
    if (value > 1) {
        return `${value} ${units}s ago`;
    }
    return `${value} ${units} ago`;
}

export function ElapsedTime({ date }) {
    return <span className="elapsed-time">{elapsedTime(date)}</span>
}
ElapsedTime.propTypes = {
    date: PropTypes.oneOfType([PropTypes.instanceOf(Date), PropTypes.number]),
}