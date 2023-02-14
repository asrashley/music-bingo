/*
Wrapper for the react-scripts scipts, that allows the current
git SHA to be passed into the scripts.
*/

const { spawn } = require('node:child_process');
const { argv, exit } = require('node:process');
const GitRevPlugin = require('git-rev-webpack-plugin');

function usage() {
  console.log(`${argv[1]} (build|start)`);
}

function getGitSha() {
  const grp = new GitRevPlugin();
  return Promise.resolve({
    branch: grp.branch(),
    commit: {
      hash: grp.hash(true),
      shortHash: grp.hash(false)
    },
    tags: grp.tag()
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
  then((gitInfo) => {
    const now = new Date();
    const buildEnv = {
      ...process.env,
      BABEL_ENV: 'production',
      NODE_ENV: 'production',
      REACT_APP_GIT_BRANCH: gitInfo.branch,
      REACT_APP_GIT_SHA: gitInfo.commit.hash,
      REACT_APP_GIT_SHORT_SHA: gitInfo.commit.shortHash,
      REACT_APP_GIT_TAGS: gitInfo.tags,
      REACT_APP_BUILD_DATE: now.toISOString()
    };
    const buildProcess = spawn("node", [`node_modules/react-scripts/scripts/${command}.js`], {
      options: 'inherit',
      env: buildEnv,
    });

    buildProcess.stdout.on('data', (data) => console.log(`${data}`) );
    buildProcess.stderr.on('data', (data) => console.error(`${data}`) );
    buildProcess.on('close', (code) => exit(code));
  });
