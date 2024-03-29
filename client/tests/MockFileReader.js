
export class MockFileReader {
  constructor(filename, error) {
    this.filename = filename;
    this.error = error;
  }

  onload = () => false;

  onerror = () => false;

  readAsText() {
    if (this.error) {
      this.onerror(this.error);
    } else {
      import(`./fixtures/${this.filename}`)
        .then((result) => {
          const event = {
            target: {
              result: JSON.stringify(result.default)
            }
          };
          this.onload(event);
        });
    }
  }
}
