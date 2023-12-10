
export const appSections = [
  'Home', 'Game', 'History', 'Clips', 'User', 'Users',
];

const routes = Object.freeze({
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  user: '/user',
  changeUser: '/user/modify',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  guestLinks: '/user/guests',
  settingsIndex: '/user/settings',
  settingsSection: '/user/settings/:section',
  listUsers: '/user/users',
  guestAccess: '/invite/:token',
  register: '/register',
  listDirectories: '/clips',
  listDirectory: '/clips/:dirPk',
  listGames: '/game',
  chooseTickets: '/game/:gameId',
  play: '/game/:gameId/tickets',
  viewTicket: '/game/:gameId/:ticketPk',
  pastGamesPopularity: '/history',
  pastGamesList: '/history/games',
  pastGamesCalendar: '/history/calendar',
  pastGamesByTheme: '/history/themes/:slug',
  gameLastUsed: '/history/themes',
  trackListingByTheme: '/history/themes/:slug/:gameId',
  trackListing: '/history/games/:gameId',
  privacy: '/privacy',
});

export default routes;
