
export function jsonResponse(payload, status = 200) {
    const body = JSON.stringify(payload);
    return {
        body,
        status,
        headers: {
            'Cache-Control': 'max-age = 0, no_cache, no_store, must_revalidate',
            'Content-Type': 'application/json',
            'Content-Length': body.length
        }
    };
}
