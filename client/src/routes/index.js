
export const appSections = [
  'Home', 'Game', 'History', 'Directories', 'User', 'Users',
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
  pastGamesList: '/history/all-games',
  pastGamesCalendar: '/history/calendar',
  gameLastUsed: '/history/last-used',
  trackListing: '/history/game/:gameId',
  privacy: '/privacy',
});

export default routes;
