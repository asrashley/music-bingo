import log from 'loglevel';

export async function* importProgressGenerator(importType) {
    const status = (phase) => {
        return ({
            "errors": [],
            "text": "",
            "pct": 0,
            "phase": 1,
            "numPhases": 1,
            "done": false,
            ...phase
        });
    };
    log.debug(`importProgressGenerator(${importType})`);
    if (importType === 'database') {
        await Promise.resolve();
        yield status({ text: 'options', pct: 1 });
        await Promise.resolve();
        yield status({ text: 'users', pct: 12 });
        await Promise.resolve();
        yield status({ text: 'albums', pct: 24 });
        await Promise.resolve();
        yield status({ text: 'artists', pct: 36 });
    }
    await Promise.resolve();
    yield status({ text: 'directories', pct: 48 });
    await Promise.resolve();
    yield status({ text: 'songs', pct: 60 });
    await Promise.resolve();
    yield status({ text: 'games', pct: 72 });
    await Promise.resolve();
    yield status({ text: 'tracks', pct: 84 });
    await Promise.resolve();
    yield status({ text: 'bingo tickets', pct: 96 });
    await Promise.resolve();
    yield status({ text: 'Import complete', pct: 100, done: true });
}
