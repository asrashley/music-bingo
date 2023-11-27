import React from 'react';
import PropTypes from 'prop-types';

import { PastGamesThemePropType } from '../types/PastGamesThemeFields';

function CalendarTableHeader({ months }) {
    const splitMonths = months.map(key => key.split('-'));
    const years = [];
    let lastYear = null;
    for (const [year] of splitMonths) {
        if (lastYear !== year) {
            years.push({ year, colSpan: 1 });
            lastYear = year;
        } else {
            years[years.length - 1].colSpan += 1;
        }
    }

    return <thead>
        <tr className="year-row">
            <th rowSpan={2} className="theme-title">Theme</th>
            {years.map(({ year, colSpan }) => <th key={year} colSpan={colSpan} className="year">{year}</th>)}
            <th rowSpan={2} className="theme-title">Theme</th>
        </tr>
        <tr className="month-row">
            {splitMonths.map(([year, month]) => <th key={`m-${year}-${month}`} className="month">{month}</th>)}
        </tr>
    </thead>
}
CalendarTableHeader.propTypes = {
    months: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
}

function CalendarCell({ value }) {
    const val = value ?? 0;
    const className = val ? 'calendar-cell active' : 'calendar-cell inactive';
    return <td className={className}>{val}</td>
}
CalendarCell.propTypes = {
    value: PropTypes.number,
};

function ThemeRow({ months, row, title }) {
    return (<tr>
        <td className="theme-title">{title}</td>
        {months.map(name => <CalendarCell key={name} value={row[name]} />)}
        <td className="theme-title">{title}</td>
    </tr>)
}
ThemeRow.propTypes = {
    title: PropTypes.string.isRequired,
    months: PropTypes.arrayOf(PropTypes.string),
    row: PropTypes.objectOf(PropTypes.number),
};

export function PastGamesCalendar({ themes, months, monthsMap }) {
    return (<table className="past-games-calendar table table-striped">
        <CalendarTableHeader months={months} />
        <tbody>
            {themes.map((theme) => <ThemeRow title={theme.title} key={theme.key} months={months} row={theme.row} />)}
        </tbody>
    </table>);
}
PastGamesCalendar.propTypes = {
    themes: PropTypes.arrayOf(PastGamesThemePropType),
    months: PropTypes.arrayOf(PropTypes.string),
};