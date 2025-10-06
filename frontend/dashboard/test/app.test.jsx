import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import path from 'path';

// Dynamically resolve the path to logo.svg to avoid brittle test dependencies
const logoSvgPath = path.resolve(__dirname, '../src/logo.svg');
vi.mock(logoSvgPath, () => ({ default: 'logo.svg' }));

const loadApp = async () => (await import('../src/App.jsx')).default;

describe('App component smoke and UX tests', () => {
  it('renders the primary call to action text', async () => {
    const App = await loadApp();
    render(<App />);
    expect(screen.getByText(/learn react/i)).toBeInTheDocument();
  });

  it('exposes the documentation link with target and rel attributes', async () => {
    const App = await loadApp();
    render(<App />);
    const link = screen.getByRole('link', { name: /learn react/i });
    expect(link).toHaveAttribute('href', 'https://reactjs.org');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('displays the instructional source file hint', async () => {
    const App = await loadApp();
    render(<App />);
    const matches = screen.getAllByText((_, element) =>
      element?.textContent?.includes('Edit src/App.js') ?? false,
    );
    expect(matches[0]).toBeVisible();
  });

  it('contains the animated logo with descriptive alt text', async () => {
    const App = await loadApp();
    render(<App />);
    const logo = screen.getByAltText(/logo/i);
    expect(logo).toBeInTheDocument();
    expect(logo.getAttribute('src')).toContain('logo');
  });

  it('wraps the experience inside the branded container', async () => {
    const App = await loadApp();
    render(<App />);
    expect(screen.getByRole('banner').parentElement).toHaveClass('App');
  });

  it('keeps the header accessible through a landmark role', async () => {
    const App = await loadApp();
    render(<App />);
    expect(screen.getByRole('banner')).toBeTruthy();
  });
});
