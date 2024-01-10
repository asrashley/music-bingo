import log from 'loglevel';

import { MockResponse } from "./MockResponse";
import { jsonResponse } from './jsonResponse';

import userData from './fixtures/user.json';
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
    const chars = 'abcdefghijklmnopqrstuvwxyz1234567890#!^';
    let token = '';
    while (token.length < length) {
        const index = Math.floor(Math.random() * chars.length);
        token += chars[index];
    }
    return token;
}

export class MockBingoServer {
    constructor(fetchMock, {
        loggedIn = false,
        currentAccessToken = 1,
        refreshToken = "refresh.token"
    } = {}) {
        this.responseModifiers = {};
        this.serverStatus = null;
        this.userDatabase = [{
            ...adminUser
        }, {
            ...normalUser
        }];
        this.guestTokens = structuredClone(guestTokens);
        this.gamesByPk = null;
        this.pastGames = [];
        this.activeGames = [];
        this.currentUser = null;
        this.currentAccessTokenId = currentAccessToken;
        this.refreshToken = refreshToken;
        if (loggedIn) {
            this.currentUser = { ...userData };
        }
        Object.assign(fetchMock.config, {
            fallbackToNetwork: false,
            warnOnFallback: true,
            Response: MockResponse,
        });
        const protectedRoute = (next) => {
            return (url, opts) => {
                if (!this.accessTokenMatches(url, opts)) {
                    return 401;
                }
                return next(url, opts);
            };
        };
        log.trace(`MockBingoServer() ${loggedIn} `);
        fetchMock
            .post('/api/refresh', this.refreshAccessToken)
            .get('/api/database', protectedRoute(this.apiRequest))
            .get('/api/directory', protectedRoute(this.apiRequest))
            .get('express:/api/directory/:dirPk', protectedRoute(this.apiRequest))
            .delete('/api/user', this.logoutUser)
            .post('/api/user/check', this.checkIfUserExists)
            .post('/api/user/reset', this.passwordResetRequest)
            .post('/api/user/modify', protectedRoute(this.modifyUser))
            .get('/api/user/guest', protectedRoute(this.getGuestTokens))
            .put('/api/user/guest/add', protectedRoute(this.addGuestAccount))
            .delete('/api/user/guest/delete/:token', protectedRoute(this.deleteGuestAccount))
            .get('/api/games', protectedRoute(this.getGames))
            .get('express:/api/game/:gamePk', protectedRoute(this.getGame))
            .get('express:/api/game/:gamePk/tickets', protectedRoute(this.getTickets))
            .get('express:/api/game/:gamePk/ticket/:ticketPk', protectedRoute(this.getTicketDetail))
            .put('express:/api/game/:gamePk/ticket/:ticketPk', protectedRoute(this.claimTicket))
            .get('express:/api/game/:gamePk/ticket/ticket-:ticketPk.pdf', protectedRoute(this.apiRequest))
            .get('express:/api/game/:gamePk/status', protectedRoute(this.getGameTicketsStatus))
            .get('express:/api/game/:gamePk/export', protectedRoute(this.apiRequest))
            .get('express:/api/song/:dirPk', protectedRoute(this.apiRequest))
            .get('/api/song', protectedRoute(this.apiRequest))
            .get('/api/settings', this.getSettings)
            .get('/api/user', this.checkUser)
            .post('/api/user', this.loginUser)
            .get('/api/users', protectedRoute(this.apiRequest));
    }

    /*
    app.add_url_rule('/api/game/<int:game_pk>/ticket/<int:ticket_pk>/cell/<int:number>',
                     view_func=api.CheckCellApi.as_view('check_cell_api'))
    */

    notFound(url) {
        return this.returnJsonResponse(url, '', 404);
    }

    apiRequest = async (url) => {
        log.debug(`apiRequest ${url}`);
        if (this.serverStatus !== null) {
            return this.serverStatus;
        }
        return this.returnJsonResponse(url, await this.fetchFixtureFile(url));
    }

    getSettings = async (url, opts) => {
        let data = await this.fetchFixtureFile(url);
        if (!this.accessTokenMatches(url, opts)) {
            log.debug('/api/settings: not logged in');
            const { privacy } = data;
            data = {
                privacy,
            };
        }
        return this.returnJsonResponse(url, data);
    }

    getGames = async (url) => {
        log.debug(`GET ${url}`);
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        return this.returnJsonResponse(url, {
            games: this.activeGames,
            past: this.pastGames,
        }, 200);
    };

    getGame = async (url) => {
        log.debug(`GET ${url}`);
        if (this.gamesByPk === null) {
            await this.loadGamesFromFixture();
        }
        const gamePk = url.split('/')[3];
        const game = await this.getGameFromPk(gamePk);
        if (game === undefined) {
            return this.notFound(url);
        }
        return this.returnJsonResponse(url, game, 200);
    };

    getTickets = async (url) => {
        log.debug(`GET ${url}`);
        const gamePk = url.split('/')[3];
        log.debug(`getTickets gamePk=${gamePk}`);
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return this.notFound(url);
        }
        return this.returnJsonResponse(url, tickets, 200);
    };

    getTicketDetail = async (url) => {
        log.debug(`GET ${url}`);
        const gamePk = url.split('/')[3];
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return this.notFound(url);
        }
        const ticketPk = parseInt(url.split('/')[5], 10);
        const ticket = tickets.find(tkt => tkt.pk === ticketPk);
        if (ticket === undefined) {
            return this.notFound(url);
        }
        if (ticket.tracks === undefined) {
            const { tracks } = await import(`./fixtures/game/${gamePk}/ticket/${ticketPk}.json`);
            ticket.tracks = tracks;
        }
        return this.returnJsonResponse(url, ticket);
    };

    claimTicket = async (url) => {
        log.debug(`claimTicket ${url}`);
        const gamePk = url.split('/')[3];
        const ticketPk = parseInt(url.split('/')[5], 10);
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return this.notFound(url);
        }
        const ticket = tickets.find(tkt => tkt.pk === ticketPk);
        if (ticket === undefined) {
            return this.notFound(url);
        }
        if (ticket.user === null) {
            ticket.user = this.currentUser.pk;
            return this.returnJsonResponse(url, '', 201);
        }
        if (ticket.user !== this.currentUser.pk) {
            // status 406 == already claimed
            return this.returnJsonResponse(url, '', 406);
        }
        return this.returnJsonResponse(url, '', 200);
    };

    getGameTicketsStatus = async (url) => {
        log.debug(`GET ${url}`);
        const gamePk = url.split('/')[3];
        const tickets = await this.getGameTicketsFromPk(gamePk);
        if (!tickets) {
            return this.notFound(url);
        }
        const claimed = {};
        for (const ticket of tickets) {
            claimed[ticket.pk] = ticket.user;
        }
        return this.returnJsonResponse(url, { claimed });
    };

    accessTokenMatches(_url, opts) {
        const { headers } = opts;
        log.trace(`Authorization = headers?.Authorization`);
        const bearer = `Bearer ${this.getAccessToken()}`;
        if (headers?.Authorization !== bearer) {
            log.debug(`Invalid access token "${headers?.Authorization}" !== "${bearer}"`);
            return false;
        }
        return true;
    }

    async fetchFixtureFile(url) {
        const filename = url.replace(/^\/api/, './fixtures');
        log.trace(`load ${filename}`);
        const data = await import(`${filename}.json`);
        //log.trace(`${filename} = ${Object.keys(data['default']).join(',')}`);
        return data['default'];
    }

    returnJsonResponse(url, data, code = 200) {
        const modFn = this.responseModifiers[url];
        if (!modFn) {
            return jsonResponse(data, code);
        }
        const modified = modFn(url, data);
        if (typeof modified === 'object') {
            if (modified?.body && modified?.status && modified?.headers) {
                // already a Response object
                return modified;
            }
        }
        return jsonResponse(modified, code);
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

    getRefreshToken() {
        return this.refreshToken;
    }

    isLoggedIn() {
        return this.currentUser !== null;
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
            accessToken: this.getAccessToken()
        };
        delete user.password;
        this.currentUser = user;
        return user;
    }

    logout() {
        this.currentUser = null;
    }

    setResponseModifier = (url, fn) => {
        this.responseModifiers[url] = fn;
    }

    setServerStatus(code) {
        this.serverStatus = code;
    }

    getAccessToken() {
        return `access.token.${this.currentAccessTokenId}`;
    }

    refreshAccessToken = () => {
        this.currentAccessTokenId++;
        log.trace(`refreshAccessToken ${this.currentAccessTokenId}`);
        return {
            'accessToken': this.getAccessToken()
        };
    };

    checkUser = async () => {
        log.debug(`checkUser loggedIn=${this.currentUser !== null}`);
        if (this.serverStatus !== null) {
            log.debug(`checkUser serverStatus=${this.serverStatus}`);
            return this.serverStatus;
        }
        if (!this.currentUser) {
            return 401;
        }
        return jsonResponse({
            ...this.currentUser,
            refreshToken: this.refreshToken,
            accessToken: this.getAccessToken(),
        });
    };

    loginUser = async (_url, opts) => {
        if (this.serverStatus !== null) {
            log.debug(`loginUser status=${this.serverStatus}`);
            return this.serverStatus;
        }
        const { username, password } = JSON.parse(opts.body);
        const user = this.login(username, password);
        if (!user) {
            return jsonResponse('', 401);
        }
        return jsonResponse(user);
    };

    logoutUser = async () => {
        if (this.serverStatus !== null) {
            log.trace(`logoutUser status=${this.serverStatus}`);
            return this.serverStatus;
        }
        log.trace('logoutUser');
        this.currentUser = null;
        return jsonResponse('Logged out');
    };

    checkIfUserExists = async (_url, opts) => {
        if (this.serverStatus !== null) {
            log.trace(`checkIfUserExists status=${this.serverStatus}`);
            return this.serverStatus;
        }
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
        return jsonResponse(response);
    };

    passwordResetRequest = async (url, opts) => {
        const body = JSON.parse(opts.body);
        const { email } = body;
        return this.returnJsonResponse(url, {
            email,
            success: true
        });
    };

    modifyUser = async (url, opts) => {
        const body = JSON.parse(opts.body);
        const { existingPassword } = body;
        if (this.currentUser.password !== existingPassword) {
            return this.jsonResponse(url, {
                success: false,
                error: "Existing password did not match",
            });
        }
        const { email, password, confirmPassword } = body;
        if (password !== confirmPassword) {
            return this.jsonResponse(url, {
                success: false,
                error: "New passwords do not match",
            });
        }
        const response = {
            email: this.currentUser.email,
            success: true,
        };
        this.currentUser = {
            ...this.currentUser,
            email,
            password,
        };
        this.userDatabase = this.userDatabase.map(usr => {
            if (usr.pk === this.currentUser.pk) {
                return this.currentUser;
            }
            return usr;
        });
        return this.returnJsonResponse(url, response);
    };

    getGuestTokens = async (url) => {
        return this.returnJsonResponse(url, this.guestTokens);
    };

    addGuestAccount = async (url) => {
        const token = {
            pk: 50 + this.guestTokens.length,
            jti: randomToken(8),
            username: randomToken(8),
            created: new Date().toDateString(),
            expires: new Date(Date.now() + 24 * 3600).toDateString(),
            revoked: false,
            user: null,
        };
        this.guestTokens.push(token);
        return this.returnJsonResponse(url, {
            success: true,
            token,
        });
    };

    deleteGuestAccount = async (url) => {
        //.delete('/api/user/guest/delete/<path:token>'
        const jti = url.split('/')[5];
        const token = this.guestTokens.find(tk => tk.jti === jti);
        if (!token) {
            return this.notFound(url);
        }
        this.guestTokens = this.guestTokens.filter(tk => tk.jti !== jti);
        return this.returnJsonResponse('', 204);
    };

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
