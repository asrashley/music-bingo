import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import GitRevPlugin from 'git-rev-webpack-plugin';
import events from 'events';
import fs from 'fs';
import readline from 'readline';

/* see https://github.com/gxmari007/vite-plugin-eslint/issues/55 */
import eslintPlugin from "@nabla/vite-plugin-eslint";

function getVersion() {
    const versionRe = /^## (\d+\.\d+\.\d+)/;

    return new Promise((resolve, reject) => {
        try {
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

async function getBuildInfo() {
    const grp = new GitRevPlugin();
    return {
        branch: grp.branch(),
        commit: {
            hash: grp.hash(true),
            shortHash: grp.hash(false)
        },
        tags: grp.tag(),
        version: await getVersion(),
    };
}

export default defineConfig(async () => {
    const buildInfo = await getBuildInfo();
    return {
        // https://github.com/vitejs/vite/issues/1973#issuecomment-787571499
        define: {
            'process.env': {},
            __BUILD_INFO__: JSON.stringify(buildInfo),
        },
        server: {
            hmr: true,
            port: 3000,
            proxy: {
                '/api': {
                    target: 'http://127.0.0.1:5000',
                    changeOrigin: true,
                },
            },
        },
        build: {
            outDir: 'build',
        },
        plugins: [
            react(),
            eslintPlugin(),
        ],
        test: {
            environment: 'jsdom',
            globals: true,
            isolate: true,
            globalSetup: './tests/global-setup.js',
            setupFiles: './tests/setup.js',
            coverage: {
                include: [
                    "src/**/*.{js,jsx,ts,tsx}",
                ],
                exclude: [
                    "src/create-tarfile.js",
                ],
                thresholds: {
                    branches: 75,
                    functions: 80,
                    lines: 75,
                    statements: 75
                }
            },
        },
    };
});