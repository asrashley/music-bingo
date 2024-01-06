import React from 'react';
import PropTypes from 'prop-types';

import { GamePropType } from '../games/types/Game';
import { TicketPropType } from '../tickets/types/Ticket';

export function Welcome({ className, game, ticket, children }) {
  return (
    <div className={className}>
      <div className="logo" />
      <div className="welcome">
        <h2 className="strapline">Like normal Bingo, but with music!</h2>
        <p className="description">Musical Bingo is a variation on the normal game of bingo, where the numbers are replaced
          with songs that the players must listen out for.</p>
        <p className="description">If you know your Bruce Springsteen from your Beyonce, your Whitney Houston from
          your Wu-Tang Clan, why not join use for a game or two?</p>
        {children}
      </div>
      <div className="number footer">Game {game.id} / Ticket {ticket.number}</div>
    </div>
  );
}

Welcome.propTypes = {
  children: PropTypes.node,
  className: PropTypes.string.isRequired,
  game: GamePropType.isRequired,
  ticket: TicketPropType.isRequired
};
