const { spawn } = require('node:child_process');
const events = require('events');
const fs = require('fs');
const readline = require('readline');

function getVersion() {
  return new Promise((resolve, reject) => {
    try {
      const versionRe = /^## (\d+\.\d+\.\d+)/;
      let found = false;
      const ac = new AbortController();
      const rl = readline.createInterface({
        input: fs.createReadStream('../CHANGELOG.md'),
        crlfDelay: Infinity,
        signal: ac.signal
      });

      rl.on('line', (line) => {
        if (found) {
          return;
        }
        const match = line.match(versionRe);
        if (match) {
          found = true;
          resolve(match[1]);
          ac.abort();
        }
      });
      events.once(rl, 'close').then(() => {
        if (!found) {
          reject('Failed to find current version number');
        }
      });
    } catch (err) {
      reject(err);
    }
  });
}

function runCommand(cmd, args, env) {
  return new Promise((resolve) => {
    console.log(`${cmd} ${args.join(' ')}`);
    const buildProcess = spawn(cmd, args, {
      options: 'inherit',
      env,
    });
    buildProcess.stdout.on('data', (data) => console.log(`${data}`));
    buildProcess.stderr.on('data', (data) => console.error(`${data}`));
    buildProcess.on('close', (code) => resolve(code));
  });
}

function createTarFile(version) {
  const tarfile = `../musicbingo-${version}.tar.gz`;
  const args = [
    '-czf', tarfile, '-C', '..', '--exclude=*.pyc',
    '--exclude=__pycache__', 'client/build', 'musicbingo',
    'Extra-Files', 'appspec.yml', 'application.py',
    'dev-requirements.txt', 'mysql-requirements.txt',
    'requirements.txt'
  ];
  return runCommand('tar', args, process.env);
}

getVersion().then(createTarFile);
