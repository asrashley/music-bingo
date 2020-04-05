export const apiServerURL = "/api";
//export const apiServerURL = `http://${window.location.hostname}:5000/api`;

export const getUserURL = `${apiServerURL}/user`;
export const getLogoutURL = `${apiServerURL}/user/logout`;
export const checkUserURL = `${apiServerURL}/user/check`;
export const registerUserURL = `${apiServerURL}/user`;
export const getGamesURL = `${apiServerURL}/games`;
export const getGameDetailURL = (gamePk) => `${apiServerURL}/games/${gamePk}`;
export const getTicketsURL = (gamePk) => `${apiServerURL}/tickets/${gamePk}`;
export const getCardURL = (gamePk, ticketPk) => `${apiServerURL}/tickets/${gamePk}/${ticketPk}`;
export const claimCardURL = (gamePk, ticketPk) => `${apiServerURL}/tickets/${gamePk}/${ticketPk}`;
export const setCardCheckedURL = (gamePk, ticketPk, number) => `/api/tickets/${gamePk}/${ticketPk}/${number}`;
export const getDownloadCardURL = (gamePk, ticketPk) => `${apiServerURL}/game/${gamePk}/get/ticket-${ticketPk}.pdf`;