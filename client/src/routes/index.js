export default {
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  user: '/user',
  changeUser: '/user/modify',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  guestLinks: '/user/guests',
  listUsers: '/user/users',
  guestAccess: '/invite/:token',
  register: '/register',
  listDirectories: '/clips',
  listDirectory: '/clips/:dirPk',
  listGames: '/game',
  chooseTickets: '/game/:gameId',
  play: '/game/:gameId/tickets',
  viewTicket: '/game/:gameId/:ticketPk',
  pastGames: '/history',
  trackListing: '/history/:gameId',
  privacy: '/privacy',
};
