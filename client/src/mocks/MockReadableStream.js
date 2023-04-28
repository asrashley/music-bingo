
export class MockReadableStream extends ReadableStream {
  constructor(parts, done) {
    super();
    this.parts = parts;
    this.textEnc = new TextEncoder();
    this.boundary = `${Date.now()}`;
    this.pos = 0;
    this.onDone = done;
  }

  read() {
    return new Promise((resolve) => {
      const done = (this.pos === this.parts.length);
      let value;
      if (!done) {
        const payload = JSON.stringify(this.parts[this.pos]);
        const headers = `Content-Type: application/json\r\nContent-Length: ${payload.length}\r\n`;
        value = `--${this.boundary}\r\n${headers}\r\n${payload}\r\n\r\n`;
        this.pos++;
        if (this.pos === this.parts.length) {
          value += `--${this.boundary}--\r\n`;
        }
        value = this.textEnc.encode(value);
      }
      resolve({
        done,
        value
      });
      if (done) {
        this.onDone();
      }
    });
  }
};

