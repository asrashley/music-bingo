import log from 'loglevel';

export function createParams(url, urlPattern) {
    let params = {};
    if (/^express:/.test(urlPattern)) {
        const patternParts = urlPattern.slice(8).split('/');
        const urlParts = url.split('/');
        urlParts.forEach((value, idx) => {
            if (idx >= patternParts.length) {
                return;
            }
            const pattern = patternParts[idx];
            const tokenIdx = pattern.indexOf(':');
            if (tokenIdx < 0) {
                return;
            }
            let bracket = pattern.indexOf('(');
            if (bracket < 1) {
                bracket = undefined;
            }
            const name = pattern.slice(tokenIdx + 1, bracket);
            params[name] = value;
        });
    } else if (urlPattern instanceof RegExp) {
        const match = urlPattern.exec(url);
        if (match?.groups) {
            params = match.groups;
        }
    }
    return params;
}

export class Router {
    constructor(fetchMock) {
        this.fetchMock = fetchMock;
    }

    delete(urlPattern, next) {
        this.mock('DELETE', urlPattern, next);
        return this;
    }

    get(urlPattern, next) {
        this.mock('GET', urlPattern, next);
        return this;
    }

    post(urlPattern, next) {
        this.mock('POST', urlPattern, next);
        return this;
    }

    put(urlPattern, next) {
        this.mock('PUT', urlPattern, next);
        return this;
    }

    mock(method, urlPattern, next) {
        const wrapper = (url, opts) => {
            log.trace(url, urlPattern);
            opts.match = urlPattern;
            opts.params = createParams(url, urlPattern);
            return next(url, opts);
        }
        this.fetchMock.mock({
            url: urlPattern,
            method
        }, wrapper);
        return this;
    }
}

