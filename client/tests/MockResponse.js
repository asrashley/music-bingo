import { Readable } from "stream";

export class MockResponse extends Response {
    constructor(...args) {
        if (args[0] instanceof ReadableStream) {
            args[0] = Readable.from(args[0]);
        }
        super(...args);
    }

    blob = async () => {
        return new Blob([this.body], {
            type: this.headers['content-type'] ?? 'application/octet-stream',
        });
    };
}

