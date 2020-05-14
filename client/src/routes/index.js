
export default {
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  register: '/register',
  game: '/game/:gameId',
  play: '/game/:gameId/tickets',
  viewTicket: '/game/:gameId/:ticketPk',
  pastGames: '/history',
  trackListing: '/history/:gameId',
  listUsers: '/users'
};

