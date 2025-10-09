import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
});

class MockResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const globalObject = globalThis as typeof globalThis & {
  ResizeObserver?: typeof MockResizeObserver;
};

if (!globalObject.ResizeObserver) {
  globalObject.ResizeObserver = MockResizeObserver;
}
