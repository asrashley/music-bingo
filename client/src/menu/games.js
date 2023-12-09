import { reverse } from 'named-urls';

import routes from '../routes';

const gamesMenuItems = [{
    href: reverse(`${routes.pastGamesPopularity}`),
    title: 'Popularity',
}, {
    href: reverse(`${routes.gameLastUsed}`),
    title: "Theme's Last Use",
}, {
    href: reverse(`${routes.pastGamesCalendar}`),
    title: 'Calendar',
}, {
    href: reverse(`${routes.pastGamesList}`),
    title: 'All Previous Games',
}];

export function getGameMenuItems(/* state, props */) {
    return gamesMenuItems;
}
