
export default {
  index: '/',
  login: '/user/login',
  logout: '/user/logout',
  passwordReset: '/user/reset',
  passwordResetConfirm: '/user/reset/:token',
  register: '/register',
  game: '/game/:gamePk',
  pastGames: '/history',
  trackListing: '/history/:gamePk',
  downloadTicket: '/game/:gamePk/:ticketPk/get',
  play: '/game/:gamePk/play',
  listUsers: '/users'
};

