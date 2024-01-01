import React from 'react';
import PropTypes from 'prop-types';

import { GameOptionsPropType } from '../../games/types/GameOptions';
import { CellPropType } from '../types/Cell';

export function BingoCell({ cell, onClick, options }) {
    const tdStyle = {
        width: `${100 / options.columns}%`,
    };
    const includeArtist = options.include_artist !== false;
    if (cell.background) {
        tdStyle.backgroundColor = cell.background;
    }
    let className = `bingo-cell ${includeArtist ? " with-artist" : "without-artist"}`;
    if (cell.checked === true) {
        className += " ticked";
    }
    return (
        <td className={className} onClick={() => onClick('click', cell)}
            onTouchStart={() => onClick('touch', cell)}
            style={tdStyle}
        >
            <div className="bingo-cell-wrap">
                <p className="title">{cell.title}</p>
                {includeArtist && <p className="artist">{cell.artist}</p>}
            </div>
        </td>
    );
}

BingoCell.propTypes = {
    cell: CellPropType.isRequired,
    onClick: PropTypes.func.isRequired,
    options: GameOptionsPropType.isRequired
};
