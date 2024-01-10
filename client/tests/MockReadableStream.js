
export class MockReadableStream extends ReadableStream {
  constructor(generator, done) {
    super();
    this.generator = generator;
    this.textEnc = new TextEncoder();
    this.boundary = `${Date.now()}`;
    this.complete = false;
    this.onDone = done;
  }

  async read() {
    if (this.complete) {
      this.onDone();
      return ({ done: true });
    }
    let { done, value } = await this.generator.next();
    if (!done) {
      const payload = JSON.stringify(value);
      const headers = `Content-Type: application/json\r\nContent-Length: ${payload.length}\r\n`;
      value = `--${this.boundary}\r\n${headers}\r\n${payload}\r\n\r\n`;
      value = this.textEnc.encode(value);
    } else {
      value = `--${this.boundary}--\r\n`;
      value = this.textEnc.encode(value);
      done = false;
      this.complete = true;
    }
    return ({
      done,
      value
    });
  }
}

