import { fixupConfigRules, fixupPluginRules } from "@eslint/compat";
import _import from "eslint-plugin-import";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";
import vitestGlobals from 'eslint-plugin-vitest-globals';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all
});

export default [...fixupConfigRules(compat.extends(
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:import/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
    "plugin:import/recommended",
    "plugin:vitest-globals/recommended",
)), {
    files: [
        "**/*.js",
        "**/*.jsx"
    ],
    ignores: [
        'vite.config.js',
        'build/*',
        'node_modules/*'
    ],
    plugins: {
        import: fixupPluginRules(_import),
        react: fixupPluginRules(react),
        "react-hooks": fixupPluginRules(reactHooks),
    },

    languageOptions: {
        globals: {
            ...globals.browser,
            ...vitestGlobals.environments.env.globals,
            vi: "readonly",
        },

        ecmaVersion: 2022,
        sourceType: "module",

        parserOptions: {
            ecmaFeatures: {
                jsx: true,
                impliedStrict: true,
            },
        },
    },

    settings: {
        react: {
            version: "18",
        },

        "import/resolver": {
            node: {
                paths: ["src"],
                extensions: [".js", ".jsx"],
            },
        },
    },

    rules: {
        "react/react-in-jsx-scope": "off",

        "no-unused-vars": ["error", {
            argsIgnorePattern: "^_",
            varsIgnorePattern: "^React$",
        }],

        "import/first": "error",
        "import/no-amd": "error",
        "import/no-anonymous-default-export": "warn",
        "react/require-render-return": "error",
        "import/no-named-as-default": "off",
    },
}];