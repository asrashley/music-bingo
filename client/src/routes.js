
export default {
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  register: '/register',
  game: '/game/:gamePk',
  play: '/game/:gamePk/tickets',
  viewTicket: '/game/:gamePk/:ticketPk',
  pastGames: '/history',
  trackListing: '/history/:gamePk',
  listUsers: '/users'
};

