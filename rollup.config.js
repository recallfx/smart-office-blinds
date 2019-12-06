import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import VuePlugin from 'rollup-plugin-vue';
import {terser} from 'rollup-plugin-terser';

const isProduction = process.env.NODE_ENV === 'production';

export default [{
  input: 'client/src/index.js',
  output: {
    file: 'client/_site/assets/script.js',
    format: 'cjs',
    name: 'sob',
    compact: isProduction,
    intro: `const NODE_ENV = "${process.env.NODE_ENV}";`,
  },
  plugins: [ 
    resolve(),
    commonjs(),
    VuePlugin(),
    isProduction && terser(),
  ],
  watch: {
    include: 'client/src/**'
  }
}];
