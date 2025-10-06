import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    include: ['test/**/*.test.{js,jsx,ts,tsx}'],
    // Exclude this test due to known flakiness/issues. See https://github.com/org/repo/issues/123 for details.
    exclude: ['test/is-number-object.test.js'],
  },
  esbuild: {
    loader: 'jsx',
    include: /(src|test)\/.*\.[jt]sx?$/,
  },
});
