/*
Wrapper for the react-scripts scipts, that allows the current
git SHA to be passed into the scripts.
*/

const { spawn } = require('node:child_process');
const { argv, exit } = require('node:process');
const GitRevPlugin = require('git-rev-webpack-plugin');
const events = require('events');
const fs = require('fs');
const readline = require('readline');

function usage() {
  console.log(`${argv[1]} (build|start)`);
}

function getCommand() {
  return new Promise((resolve, reject) => {
    const command = argv[2];
    if (command !== "build" && command !== "start") {
      usage();
      reject(`Unknown command ${command}`);
    } else {
      resolve({ command });
    }
  });
}

function getBuildInfo(props) {
  const grp = new GitRevPlugin();
  return Promise.resolve({
    ...props,
    buildInfo: {
      branch: grp.branch(),
      commit: {
        hash: grp.hash(true),
        shortHash: grp.hash(false)
      },
      tags: grp.tag()
    }
  });
}

function getVersion(props) {
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
          resolve({
            ...props,
            version: match[1]
          });
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

function createTarFile(props) {
  if (props.exitCode !== 0 || props.command !== 'build') {
    return Promise.resolve(props);
  }
  const { buildInfo } = props;
  const tarfile = `../musicbingo-${buildInfo.branch}.tar.gz`;
  const args = [
    '-czf', tarfile, '-C', '..', '--exclude=*.pyc',
    '--exclude=__pycache__', 'client/build', 'musicbingo',
    'Extra-Files', 'appspec.yml', 'application.py',
    'dev-requirements.txt', 'mysql-requirements.txt',
    'requirements.txt'
  ];
  return runCommand('tar', args, process.env)
    .then(code => ({
      ...props,
      exitCode: code
    }));
}

function runReactScript(props) {
  const { buildInfo, command, version } = props;
  const { branch, commit, tags } = buildInfo;
  const now = new Date();
  const buildEnv = {
    ...process.env,
    BABEL_ENV: 'production',
    NODE_ENV: 'production',
    REACT_APP_GIT_BRANCH: branch,
    REACT_APP_GIT_SHA: commit.hash,
    REACT_APP_GIT_SHORT_SHA: commit.shortHash,
    REACT_APP_GIT_TAGS: tags,
    REACT_APP_BUILD_DATE: now.toISOString(),
    REACT_APP_VERSION: version
  };
  return runCommand('node', [`node_modules/react-scripts/scripts/${command}.js`], buildEnv)
    .then((exitCode) => ({
      now,
      buildInfo,
      exitCode
    }));
}

if (argv.length < 3) {
  usage();
  exit(1);
}

getCommand()
  .then(getBuildInfo)
  .then(getVersion)
  .then(runReactScript)
  .then(createTarFile)
  .then(({ exitCode }) => exit(exitCode))
  .catch(err => {
    console.error(err);
    exit(1);
  });
