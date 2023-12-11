import React from 'react';
import PropTypes from 'prop-types';

import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import routes from '../../routes';

export function PastGamesButtons({ page }) {
    return <div className="past-games-buttons">
        <div className={`row mb-4 page-${page}`}>
            <div className="col text-center">
                <Link to={reverse(`${routes.pastGamesPopularity}`)}
                    className="btn btn-lg btn-light border border-dark-subtle popularity-button">
                    <h4>Theme Popularity</h4>
                </Link>
            </div>
            <div className="col text-center">
                <Link to={reverse(`${routes.gameLastUsed}`)}
                    className="btn btn-lg btn-light border border-dark-subtle usage-button">
                    <h4>Theme Last Usage</h4>
                </Link>
            </div>
            <div className="col text-center">
                <Link to={reverse(`${routes.pastGamesCalendar}`)}
                    className="btn btn-lg btn-light border border-dark-subtle calendar-button">
                    <h4>Games Calendar</h4>
                </Link>
            </div>
            <div className="col text-center">
                <Link to={reverse(`${routes.pastGamesList}`)}
                    className="btn btn-lg btn-light border border-dark-subtle all-button">
                    <h4>All Games</h4>
                </Link>
            </div>
        </div>
    </div>;
}
PastGamesButtons.propTypes = {
    page: PropTypes.oneOf(['all', 'calendar', 'popularity', 'usage']).isRequired,
}