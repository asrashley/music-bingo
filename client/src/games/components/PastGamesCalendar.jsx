import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { PastGamesThemePropType } from '../types/PastGamesThemeFields';
import routes from '../../routes';

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
    months: PropTypes.arrayOf(PropTypes.string),
}

function CalendarCell({ value }) {
    const val = value ?? 0;
    const className = val ? 'calendar-cell active' : 'calendar-cell inactive';
    return <td className={className}>{val}</td>
}
CalendarCell.propTypes = {
    value: PropTypes.number,
};

function TitleCell({ slug, title }) {
    return (<td className="theme-title">
        <Link to={reverse(`${routes.pastGamesByTheme}`, { slug })}>
            {title}
        </Link>
    </td>);
}
TitleCell.propTypes = {
    slug: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
}

function ThemeRow({ months, theme }) {
    const { slug, row, title } = theme;
    return (<tr>
        <TitleCell key={`before-${slug}`} slug={slug} title={title} />
        {months.map(name => <CalendarCell key={name} value={row[name]} />)}
        <TitleCell key={`after-${slug}`} slug={slug} title={title} />
    </tr>)
}
ThemeRow.propTypes = {
    theme: PastGamesThemePropType.isRequired,
    months: PropTypes.arrayOf(PropTypes.string),
};

export function PastGamesCalendar({ themes, months, monthsMap }) {
    return (<table className="past-games-calendar table table-striped">
        <CalendarTableHeader months={months} />
        <tbody>
            {themes.map((theme) => <ThemeRow theme={theme} key={theme.slug} months={months} />)}
        </tbody>
    </table>);
}
PastGamesCalendar.propTypes = {
    themes: PropTypes.arrayOf(PastGamesThemePropType),
    months: PropTypes.arrayOf(PropTypes.string),
};

export const PastGamesCalendarPropType = PropTypes.shape({
    themes: PropTypes.arrayOf(PastGamesThemePropType),
    months: PropTypes.arrayOf(PropTypes.string),
});