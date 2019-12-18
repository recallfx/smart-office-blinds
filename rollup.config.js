import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import VuePlugin from 'rollup-plugin-vue';
import { terser } from 'rollup-plugin-terser';
import json from '@rollup/plugin-json';
import ignore from 'rollup-plugin-ignore';

const isProduction = process.env.NODE_ENV === 'production';

export default [
  {
    input: 'client/src/index.js',
    output: {
      file: 'client/_site/assets/script.js',
      format: 'cjs',
      name: 'sob-client',
      compact: isProduction,
      intro: `const NODE_ENV = "${process.env.NODE_ENV}";`,
    },
    plugins: [
      json({ preferConst: true }),
      resolve(),
      commonjs(),
      VuePlugin(),
      isProduction && terser(),
    ],
    watch: {
      include: 'client/src/**',
    },
  },
  {
    input: 'functions/src/index.js',
    output: {
      file: 'functions/index.js',
      format: 'cjs',
      name: 'sob-functions',
      compact: isProduction,
      intro: `const NODE_ENV = "${process.env.NODE_ENV}";`,
    },
    plugins: [
      ignore('firebase-functions', 'firebase-admin', 'axios'),
      json({ preferConst: true }),
      resolve(),
      commonjs(),
    ],
    watch: {
      include: 'functions/src/**',
    },
  },
];
