export const apiServerURL = "/api";
//export const apiServerURL = `http://${window.location.hostname}:5000/api`;

export const getUserURL = `${apiServerURL}/user`;
export const getLogoutURL = `${apiServerURL}/user/logout`;
export const checkUserURL = `${apiServerURL}/user/check`;
export const registerUserURL = `${apiServerURL}/user`;
export const passwordResetUserURL = `${apiServerURL}/user/reset`;
export const getGamesURL = `${apiServerURL}/games`;
export const getGameDetailURL = (gamePk) => `${apiServerURL}/games/${gamePk}`;
export const listTicketsURL = (gamePk) => `${apiServerURL}/game/${gamePk}`;
export const getTicketsStatusURL = (gamePk) => `${apiServerURL}/game/${gamePk}/status`;
export const getCardURL = (gamePk, ticketPk) => `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`;
export const claimCardURL = (gamePk, ticketPk) => `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}`;
export const setCardCheckedURL = (gamePk, ticketPk, number) => `${apiServerURL}/game/${gamePk}/ticket/${ticketPk}/cell/${number}`;
export const getDownloadCardURL = (gamePk, ticketPk) => `${apiServerURL}/game/${gamePk}/ticket/ticket-${ticketPk}.pdf`;