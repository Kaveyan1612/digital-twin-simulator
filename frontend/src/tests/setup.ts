import '@testing-library/jest-dom';
import { vi } from 'vitest';

vi.mock('zustand', () => ({
  create: (fn: any) => {
    let state: any = {};
    const listeners = new Set<() => void>();
    const store = {
      getState: () => state,
      setState: (partial: any) => {
        state = typeof partial === 'function' ? partial(state) : { ...state, ...partial };
        listeners.forEach(l => l());
      },
      subscribe: (listener: () => void) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
      },
    };
    return fn(store.setState, store.getState, store);
  },
}));

global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));