export default {
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  user: '/user',
  changeUser: '/user/modify',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  register: '/register',
  listGames: '/game',
  chooseTickets: '/game/:gameId',
  play: '/game/:gameId/tickets',
  viewTicket: '/game/:gameId/:ticketPk',
  pastGames: '/history',
  trackListing: '/history/:gameId',
  privacy: '/privacy',
  listUsers: '/users'
};
