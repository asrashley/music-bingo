/*
Wrapper for the react-scripts scipts, that allows the current
git SHA to be passed into the scripts.
*/

const { exec, spawn } = require('node:child_process');
const { argv, exit } = require('node:process');

function usage() {
  console.log(`${argv[1]} (build|start)`);
}

function getGitSha() {
  return new Promise((resolve, reject) => {
    const gitSha = [];
    const err = [];
    const gitCmd = spawn('git', ['rev-parse', 'HEAD']);
    gitCmd.stdout.on('data', (data) => gitSha.push(data));
    gitCmd.stderr.on('data', (data) => err.push(data));
    gitCmd.on('close', (code) => {
      if (code === 0) {
        resolve(gitSha.join('').trim());
      }
      reject(`git command failed with code ${code}: ${err.join('')}`);
    });
  });
}

if (argv.length < 3) {
  usage();
  exit(1);
}

const command = argv[2];

if (command !== "build" && command !== "start") {
  console.error(`Unknown command ${command}`);
  usage();
  exit(1);
}

getGitSha().
  then((gitSha) => {
    const now = new Date();
    const buildEnv = {
      ...process.env,
      BABEL_ENV: 'production',
      NODE_ENV: 'production',
      REACT_APP_GIT_SHA: gitSha,
      REACT_APP_GIT_SHORT_SHA: gitSha.slice(0,8),
      REACT_APP_BUILD_DATE: now.toISOString(),
    };
    console.log(`gitSha=${gitSha}`);
    console.log(`buildTime=${now}`);
    /*console.log(`${JSON.stringify(buildEnv)}`);*/

    const buildProcess = spawn("node", [`node_modules/react-scripts/scripts/${command}.js`], {
      options: 'inherit',
      env: buildEnv,
    });

    buildProcess.stdout.on('data', (data) => console.log(`${data}`) );
    buildProcess.stderr.on('data', (data) => console.error(`${data}`) );
    buildProcess.on('close', (code) => exit(code));
  });
