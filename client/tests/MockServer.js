import log from 'loglevel';

import { jsonResponse } from './jsonResponse';
import { MockResponse } from './MockResponse';

import userData from './fixtures/user.json';
import userState from './fixtures/userState.json';
import guestTokens from './fixtures/user/guest.json';

export const adminUser = {
    ...userData,
    password: 'sup3r$ecret!',
};

export const normalUser = {
    ...userData,
    pk: 100,
    username: 'user',
    email: 'a.user@example.tld',
    password: 'mysecret',
    "groups": ["users"],
};

function randomToken(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ_=+';
    let token = '';
    while (token.length < length) {
        const index = Math.floor(Math.random() * chars.length);
        token += chars[index];
    }
    return token;
}

function isPromise(item) {
    return (typeof item === 'object' && typeof item?.then === 'function' && typeof item?.catch === 'function');
}

export class MockBingoServer {
    constructor(fetchMock, {
        loggedIn = false,
        currentUser = null,
    } = {}) {
        this.fetchMock = fetchMock;
        this.responseModifiers = {};
        this.pendingPromises = {};
        this.serverStatus = null;
        this.isShutdown = false;
        this.userDatabase = [{
            ...adminUser
        }, {
            ...normalUser
        }];
        this.guestTokens = structuredClone(guestTokens);
        this.gamesByPk = null;
        this.pastGames = [];
        this.activeGames = [];
        this.nextAccessTokenId = 1;
        this.nextRefreshTokenId = 1000;
        if (loggedIn && !currentUser) {
            currentUser = adminUser;
        }
        if (currentUser) {
            let user = this.userDatabase.find(
                user => user.username === currentUser.username || user.email === currentUser.email);
            if (!user) {
                user = { ...currentUser };
                this.userDatabase.push(user);
            }
            user.refreshToken = this.generateRefreshToken();
            user.accessToken = this.generateAccessToken();
        }

        Object.assign(fetchMock.config, {
            fallbackToNetwork: false,
            warnOnFallback: true,
            Response: MockResponse,
        });

        const returnJsonResponse = (url, opts) => {
            return async (data, code = 200) => {
                if (this.isShutdown) {
                    return 503;
                }
                const key = `${opts.method}.${url}`;
                const modFn = this.responseModifiers[key];
                if (!modFn) {
                    return jsonResponse(data, code);
                }
                let modified = modFn(url, opts, data);
                if (typeof modified === 'object') {
                    if (isPromise(modified)) {
                        modified = await modified;
                        if (this.isShutdown) {
                            return 503;
                        }
                    }
                    if (modified?.body && modified?.status && modified?.headers) {
                        // already a Response object
                        return modified;
                    }
                }
                return jsonResponse(modified, code);
            };
        };

        const checkPending = (next) => {
            return (url, opts) => {
                const response = next(url, opts);
                const key = `${opts.method}.${url}`;
                if (this.pendingPromises && this.pendingPromises[key]) {
                    const { resolve } = this.pendingPromises[key];
                    delete this.pendingPromises[key];
                    if (isPromise(response)) {
                        return response.then((nextResponse) => {
                            resolve(nextResponse);
                            return nextResponse;
                        });
                    }
                    resolve(response);
                }
                return response;
            };
        };

        const serverStatus = (next) => {
            return checkPending((url, opts) => {
                log.debug(`${opts.method}: ${url}`);
                if (this.serverStatus !== null) {
                    log.debug(`serverStatus=${serverStatus}`);
                    return this.serverStatus;
                }
                const newOpts = {
                    ...opts,
                    jsonResponse: returnJsonResponse(url, opts),
                    notFound: () => {
                        return opts.jsonResponse('', 404);
                    },
                };
                return next(url, newOpts);
            });
        };

        const protectedRoute = (next) => {
            return serverStatus((url, opts) => {
                if (!this.getUserFromAccessToken(opts)) {
                    return 401;
                }
                return next(url, opts);
            });
        };

        fetchMock
            .post('/api/refresh', serverStatus(this.refreshAccessToken))
            .get('/api/database', protectedRoute(this.apiRequest))
            .get('/api/directory', protectedRoute(this.apiRequest))
            .get('express:/api/directory/:dirPk', protectedRoute(this.apiRequest))
            .delete('/api/user', serverStatus(this.logoutUser))
            .put('/api/user', serverStatus(this.addUserApi))
            .post('/api/user/check', serverStatus(this.checkIfUserExists))
            .post('/api/user/reset', serverStatus(this.passwordResetRequest))
            .post('/api/user/modify', protectedRoute(this.modifyUser))
            .get('/api/user/guest', protectedRoute(this.getGuestTokens))
            .post('/api/user/guest', serverStatus(this.checkGuestToken))
            .put('/api/user/guest', serverStatus(this.createGuestAccount))
            .put('/api/user/guest/add', protectedRoute(this.addGuestToken))
            .delete('express:/api/user/guest/delete/:token', protectedRoute(this.deleteGuestAccount))
            .get('/api/games', protectedRoute(this.getGames))
            .get('express:/api/game/:gamePk', protectedRoute(this.getGame))
            .post('express:/api/game/:gamePk', protectedRoute(this.modifyGame))
            .delete('express:/api/game/:gamePk', protectedRoute(this.deleteGame))
            .get('express:/api/game/:gamePk/tickets', protectedRoute(this.getTickets))
            .get('express:/api/game/:gamePk/ticket/:ticketPk', protectedRoute(this.getTicketDetail))
            .put('express:/api/game/:gamePk/ticket/:ticketPk', protectedRoute(this.claimTicket))
            .get('express:/api/game/:gamePk/ticket/ticket-:ticketPk.pdf', protectedRoute(this.apiRequest))
            .get('express:/api/game/:gamePk/status', protectedRoute(this.getGameTicketsStatus))
            .get('express:/api/game/:gamePk/export', protectedRoute(this.apiRequest))
            .get('express:/api/song/:dirPk', protectedRoute(this.apiRequest))
            .get('/api/song', protectedRoute(this.apiRequest))
            .get('/api/settings', serverStatus(this.getSettings))
            .get('/api/user', serverStatus(this.checkUser))
            .post('/api/user', serverStatus(this.loginUser))
            .get('/api/users', protectedRoute(this.apiRequest));
    }
    /*
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>/cell/<int:number>',
                     view_func=api.CheckCellApi.as_view('check_cell_api'))
    */

    //
    // public methods
    //

    shutdown() {
        this.isShutdown = true;
        this.serverStatus = 503; // service unavailable
        this.fetchMock.reset();
        for (const [url, { reject }] of Object.entries(this.pendingPromises)) {
            reject(new Error(url));
        }
        this.pendingPromises = null;
        this.fetchMock = null;
    }

    addUser(user) {
        this.userDatabase.push(user);
    }

    login(username, password) {
        const dbEntry = this.userDatabase.find(item => (item.username === username && item.password === password));
        log.debug(`loginUser: username="${username}" password="${password}" entry=${dbEntry}`);
        if (!dbEntry) {
            return null;
        }
        const user = {
            ...userData,
            ...dbEntry,
            refreshToken: this.refreshToken,
            accessToken: this.generateAccessToken()
        };
        delete user.password;
        this.userDatabase = this.userDatabase.map(usr => {
            if (usr.pk === user.pk) {
                return user;
            }
            return usr;
        });
        return user;
    }

    setResponseModifier = (url, method, fn) => {
        const key = `${method.toUpperCase()}.${url}`;
        this.responseModifiers[key] = fn;
    }

    addResponsePromise(url, method) {
        const key = `${method.toUpperCase()}.${url}`;
        return new Promise((resolve, reject) => {
            this.pendingPromises[key] = { resolve, reject };
        });
    }

    setServerStatus(code) {
        this.serverStatus = code;
    }

    getUser({ email, username }) {
        return this.userDatabase.find(usr => usr.username === username || usr.email === email);
    }

    isLoggedIn({ email, username }) {
        const user = this.getUser({ email, username });
        return user && user.accessToken !== null;
    }

    getUserState({ email, username }) {
        const userDb = this.userDatabase.find(usr => usr.username === username || usr.email === email);
        if (!userDb) {
            throw new Error(`Unknown user email=${email} username=${username}`);
        }
        const user = {
            ...userState,
            ...userDb,
            groups: {},
        };
        userDb.groups.forEach(g => user.groups[g] = true);
        return user;
    }

    //
    // JSON REST API
    //

    refreshAccessToken = (url, opts) => {
        const { headers } = opts;
        if (!headers?.Authorization) {
            return this.returnJsonResponse('Missing Authorization header', 401);
        }
        const token = headers.Authorization.split(' ')[1];
        const user = this.userDatabase.find(usr => usr.refreshToken === token);
        if (!user) {
            return this.returnJsonResponse('Refresh token mismatch', 401);
        }
        log.trace(`refreshAccessToken ${user.username}`);
        user.accessToken = this.generateAccessToken();
        return opts.jsonResponse({
            'accessToken': user.accessToken,
        });
    };

    apiRequest = async (url, opts) => {
        return opts.jsonResponse(await this.fetchFixtureFile(url));
    }

    getSettings = async (url, opts) => {
        let data = await this.fetchFixtureFile(url);
        if (!this.getUserFromAccessToken(opts)) {
            log.debug('/api/settings: not logged in');
            const { privacy } = data;
            data = {
                privacy,
            };
        }
        return opts.jsonResponse(data);
    }

    getGames = async (_url, opts) => {
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        return opts.jsonResponse({
            games: this.activeGames,
            past: this.pastGames,
        }, 200);
    };

    getGame = async (url, opts) => {
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        const gamePk = url.split('/')[3];
        const game = await this.getGameFromPk(gamePk);
        if (game === undefined) {
            return opts.notFound();
        }
        return opts.jsonResponse(game, 200);
    };

    modifyGame = async (url, opts) => {
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        const gamePk = url.split('/')[3];
        const game = await this.getGameFromPk(gamePk);
        if (game === undefined) {
            return opts.notFound();
        }
        const {
            start = game.start,
            end = game.end,
            options = game.options,
            title = game.title } = JSON.parse(opts.body);
        const modifiedGame = {
            ...game,
            end,
            options,
            start,
            title,
        };
        this.activeGames = this.activeGames.map(g => {
            if (g.pk === modifiedGame.pk) {
                return modifiedGame;
            }
            return g;
        });
        this.pastGames = this.pastGames.map(g => {
            if (g.pk === modifiedGame.pk) {
                return modifiedGame;
            }
            return g;
        });
        return opts.jsonResponse({
            success: true,
            game: modifiedGame
        });
    };

    deleteGame = async (url, opts) => {
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        const gamePk = url.split('/')[3];
        const game = await this.getGameFromPk(gamePk);
        if (game === undefined) {
            return opts.notFound();
        }
        const pk = parseInt(gamePk, 10);
        this.pastGames = this.pastGames.filter(g => g.pk !== pk);
        this.activeGames = this.activeGames.filter(g => g.pk !== pk);
        delete this.gamesByPk[gamePk];
        return opts.jsonResponse('', 204);
    };

    getTickets = async (url, opts) => {
        const gamePk = url.split('/')[3];
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return opts.notFound();
        }
        return opts.jsonResponse(tickets, 200);
    };

    getTicketDetail = async (url, opts) => {
        const gamePk = url.split('/')[3];
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return opts.notFound();
        }
        const ticketPk = parseInt(url.split('/')[5], 10);
        const ticket = tickets.find(tkt => tkt.pk === ticketPk);
        if (ticket === undefined) {
            return opts.notFound();
        }
        if (ticket.tracks === undefined) {
            const { tracks } = await import(`./fixtures/game/${gamePk}/ticket/${ticketPk}.json`);
            ticket.tracks = tracks;
        }
        return opts.jsonResponse(ticket);
    };

    claimTicket = async (url, opts) => {
        log.debug(`claimTicket ${url}`);
        const gamePk = url.split('/')[3];
        const ticketPk = parseInt(url.split('/')[5], 10);
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return opts.notFound();
        }
        const ticket = tickets.find(tkt => tkt.pk === ticketPk);
        if (ticket === undefined) {
            return opts.notFound();
        }
        if (ticket.user === null) {
            ticket.user = opts.currentUser.pk;
            return opts.jsonResponse('', 201);
        }
        if (ticket.user !== opts.currentUser.pk) {
            // status 406 == already claimed
            return opts.jsonResponse('', 406);
        }
        return opts.jsonResponse('', 200);
    };

    getGameTicketsStatus = async (url, opts) => {
        log.debug(`GET ${url}`);
        const gamePk = url.split('/')[3];
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return opts.notFound();
        }
        const claimed = {};
        for (const ticket of tickets) {
            claimed[ticket.pk] = ticket.user;
        }
        return opts.jsonResponse({ claimed });
    };

    checkUser = async (url, opts) => {
        log.debug(`checkUser user=${opts.currentUser?.username}`);
        if (!opts.currentUser) {
            return 401;
        }
        return opts.jsonResponse(opts.currentUser);
    };

    loginUser = async (url, opts) => {
        const { username, password } = JSON.parse(opts.body);
        const user = this.login(username, password);
        if (!user) {
            return opts.jsonResponse('', 401);
        }
        return opts.jsonResponse(user);
    };

    logoutUser = async (url, opts) => {
        log.trace('logoutUser');
        const user = this.getUserFromAccessToken(opts);
        if (user) {
            user.accessToken = null;
        }
        return opts.jsonResponse('Logged out');
    };

    checkIfUserExists = async (url, opts) => {
        const { username, email } = JSON.parse(opts.body);
        const response = {
            "username": false,
            "email": false
        };
        this.userDatabase.forEach((item) => {
            if (item.username === username) {
                response.username = true;
            }
            if (item.email === email) {
                response.email = true;
            }
        });
        log.debug(`checkIfUserExists username=${username} email=${email} response=${JSON.stringify(response)}`);
        return opts.jsonResponse(response);
    };

    passwordResetRequest = async (url, opts) => {
        const body = JSON.parse(opts.body);
        const { email } = body;
        return opts.jsonResponse({
            email,
            success: true
        });
    };

    addUserApi = (url, opts) => {
        const { email, username, password } = JSON.parse(opts.body);
        if (this.userDatabase.some(usr => usr.email === email || usr.username === username)) {
            return opts.jsonResponse({
                error: {
                    username: `Username ${username} is already taken, choose another one`,
                },
                success: false,
                user: {
                    username,
                    email,
                }
            });
        }
        const user = {
            ...normalUser,
            email,
            username,
            password,
            groups: ["users"],
            accessToken: this.generateAccessToken(),
            refreshToken: this.generateRefreshToken(),
        };
        this.userDatabase.push({ ...user });
        delete user.password;
        return opts.jsonResponse({
            message: 'Successfully registered',
            success: true,
            user,
            accessToken: user.accessToken,
            refreshToken: user.refreshToken,
        });
    };

    modifyUser = async (url, opts) => {
        const body = JSON.parse(opts.body);
        const { existingPassword } = body;
        if (opts.currentUser?.password !== existingPassword) {
            return opts.jsonResponse({
                success: false,
                error: "Existing password did not match",
            });
        }
        const { email, password, confirmPassword } = body;
        if (password !== confirmPassword) {
            return opts.jsonResponse({
                success: false,
                error: "New passwords do not match",
            });
        }
        const response = {
            email,
            success: true,
        };
        opts.currentUser = {
            ...opts.currentUser,
            email,
            password,
        };
        this.userDatabase = this.userDatabase.map(usr => {
            if (usr.pk === opts.currentUser.pk) {
                return opts.currentUser;
            }
            return usr;
        });
        return opts.jsonResponse(response);
    };

    getGuestTokens = async (_url, opts) => {
        return opts.jsonResponse(this.guestTokens);
    };

    checkGuestToken = async (_url, opts) => {
        const body = JSON.parse(opts.body);
        const { token: jti } = body;
        if (!jti) {
            log.debug(`checkGuestToken token "${opts.body}" missing from request`);
            return opts.jsonResponse('Guest token missing', 400)
        }
        return opts.jsonResponse({
            success: this.guestTokens.some(gt => gt.jti === jti)
        });
    };

    addGuestToken = async (_url, opts) => {
        const token = {
            pk: 50 + this.guestTokens.length,
            jti: randomToken(8),
            username: randomToken(8),
            created: new Date().toDateString(),
            expires: new Date(Date.now() + 24 * 3600).toDateString(),
            revoked: false,
            token_type: 3,
            user: null,
        };
        this.guestTokens.push(token);
        return opts.jsonResponse({
            success: true,
            token,
        });
    };

    createGuestAccount = async (url, opts) => {
        const body = JSON.parse(opts.body);
        const { token: jti } = body;
        if (!jti) {
            return opts.jsonResponse('Guest token missing', 400)
        }
        const token = this.guestTokens.find(gt => gt.jti === jti);
        if (!token) {
            return opts.jsonResponse({
                success: false,
                error: "Unknown guest token",
            });
        }
        let username = null;
        let guestId = 100;
        while (!username) {
            username = `guest${guestId}`;
            if (this.userDatabase.some(usr => usr.username === username)) {
                username = null;
                guestId++;
            }
        }
        const user = {
            ...normalUser,
            username,
            password: randomToken(14),
            email: username,
            groups: ['guests'],
            last_login: Date.now(),
        };
        this.userDatabase.push(user);
        const result = {
            ...user,
            success: true,
            accessToken: this.generateAccessToken(),
            refreshToken: this.generateRefreshToken(),
        };
        return opts.jsonResponse(result);
    };

    deleteGuestAccount = async (url, opts) => {
        const jti = url.split('/')[5];
        const token = this.guestTokens.find(tk => tk.jti === jti);
        if (!token) {
            return opts.notFound();
        }
        this.guestTokens = this.guestTokens.filter(tk => tk.jti !== jti);
        return opts.jsonResponse('', 204);
    };

    //
    // private methods
    //

    getUserFromAccessToken(opts) {
        const { headers } = opts;
        log.trace(`Authorization = ${headers?.Authorization}`);
        if (!headers?.Authorization) {
            return null;
        }
        const token = headers.Authorization.split(' ')[1];
        const user = this.userDatabase.find(usr => usr.accessToken === token);
        if (user) {
            opts.currentUser = user;
        }
        return user;
    }

    async fetchFixtureFile(url) {
        const filename = url.replace(/^\/api/, './fixtures');
        log.trace(`load fixture ${filename}.json`);
        const data = await import(`${filename}.json`);
        //log.trace(`${filename} = ${Object.keys(data['default']).join(',')}`);
        return data['default'];
    }

    async getGameTicketsFromPk(gamePk) {
        const game = await this.getGameFromPk(gamePk);
        if (!game) {
            return null;
        }
        if (game.tickets === undefined) {
            const tickets = await import(`./fixtures/game/${gamePk}/tickets.json`);
            game.tickets = structuredClone(tickets['default']);
        }
        return game.tickets ?? null;
    }

    async claimTicketForUser(gamePk, ticketPk, user) {
        const game = await this.getGameFromPk(gamePk);
        if (game === undefined) {
            return false;
        }
        if (game.tickets === undefined) {
            const tickets = await import(`./fixtures/game/${gamePk}/tickets.json`);
            game.tickets = tickets['default'];
        }
        const ticket = game.tickets.find(tkt => tkt.pk === ticketPk);
        if (ticket === undefined) {
            return false;
        }
        if (ticket.user !== null && ticket.user !== user.pk) {
            return false;
        }
        ticket.user = user.pk;
        return true;
    }

    generateAccessToken() {
        return `access.token.${this.nextAccessTokenId++}`;
    }

    generateRefreshToken() {
        return `refresh.token.${this.nextRefreshTokenId++}`;
    }

    async loadGamesFromFixture() {
        log.debug('loadGamesFromFixture');
        const { games, past } = await import('./fixtures/games.json');
        this.gamesByPk = {};
        this.activeGames = structuredClone(games);
        this.pastGames = structuredClone(past);
        this.activeGames.forEach(g => {
            this.gamesByPk[g.pk] = g;
        });
        this.pastGames.forEach(g => {
            this.gamesByPk[g.pk] = g;
        });
    }

    async getGameFromPk(gamePk) {
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        return this.gamesByPk[gamePk];
    }
}
