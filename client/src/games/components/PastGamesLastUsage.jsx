import React, { useReducer, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Table, Column, HeaderCell } from 'rsuite-table';
import { reverse } from 'named-urls';

import { DateTimeCell, ElapsedTimeCell, LinkCell } from '../../components';
import { PastGamesThemePropType } from '../types/PastGamesThemeFields';

import { routes } from '../../routes/routes';

/* MonthDetail is a map of theme key to game count */
export const MonthDetail = PropTypes.objectOf(PropTypes.number);

export function sortData(data, sortColumn, sortType) {
    const result = [...data];
    result.sort((a, b) => {
        if (a[sortColumn] < b[sortColumn]) {
            return (sortType === "desc") ? -1 : 1;
        }
        if (a[sortColumn] > b[sortColumn]) {
            return (sortType === "desc") ? 1 : -1;
        }
        return 0;
    });
    return result;
}

function reducer(state, action) {
    switch (action.type) {
        case 'setData':
            return {
                ...state,
                data: action.data,
            };
        case 'setSort': {
            const { data, sortColumn, sortType } = action;
            return {
                ...state,
                sortColumn,
                sortType,
                data: sortData(data, sortColumn, sortType),
            };
        }
        default:
            return state;
    }
}

export function PastGamesLastUsage({ loading, themes }) {
    const [state, dispatch] = useReducer(reducer, {
        sortColumn: 'theme',
        sortType: 'desc',
        data: themes ?? [],
    });
    const { sortColumn, sortType, data } = state;

    useEffect(() => {
        dispatch({ type: 'setData', data: themes });
    }, [themes]);

    const pastGamesLink = (theme) => {
        return reverse(`${routes.pastGamesByTheme}`, { slug: theme.slug });
    }

    return (<Table
        className="past-games-calendar table table-striped"
        title="Theme History"
        rowKey='slug'
        autoHeight
        bordered
        cellBordered
        loading={loading}
        data={data}
        sortColumn={sortColumn}
        sortType={sortType}
        onSortColumn={(sortColumn, sortType) => dispatch({ type: 'setSort', sortColumn, sortType, data })}
        width={350 + 400}
    >
        <Column width={350} align="left" sortable fixed resizable>
            <HeaderCell>Theme</HeaderCell>
            <LinkCell dataKey="title" to={pastGamesLink} />
        </Column>
        <Column width={200} align="right" sortable fixed>
            <HeaderCell>Last Used</HeaderCell>
            <DateTimeCell dataKey="lastUsed" />
        </Column>
        <Column width={200} align="right" sortable fixed>
            <HeaderCell>Elapsed Time</HeaderCell>
            <ElapsedTimeCell dataKey="elapsedTime" />
        </Column>
    </Table>);
}
PastGamesLastUsage.propTypes = {
    themes: PropTypes.arrayOf(PastGamesThemePropType),
    loading: PropTypes.bool.isRequired,
};
