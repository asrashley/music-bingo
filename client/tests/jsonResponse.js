
export function jsonResponse(payload, status = 200) {
    const body = status !== 204 ? JSON.stringify(payload) : undefined;
    const contentLength = status !== 204 ? body.length : 0;
    return {
        body,
        status,
        headers: {
            'Cache-Control': 'max-age = 0, no_cache, no_store, must_revalidate',
            'Content-Type': 'application/json',
            'Content-Length': contentLength,
        },
    };
}
