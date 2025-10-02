# Contributing to Commercial-View

Thank you for your interest in contributing to Commercial-View! This document provides guidelines and best practices for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/Commercial-View.git
   cd Commercial-View
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Build the Project**
   ```bash
   npm run build
   ```

4. **Run Linting**
   ```bash
   npm run lint
   ```

## Code Standards

### TypeScript Guidelines

- Use strict TypeScript configuration
- Always define proper types and interfaces
- Avoid using `any` type
- Document all public APIs with JSDoc comments
- Use meaningful variable and function names

### Code Style

- Follow the ESLint configuration provided
- Use 2 spaces for indentation
- Maximum line length: 100 characters
- Use single quotes for strings
- Add trailing commas in multiline objects/arrays

### Documentation

- All public APIs must have JSDoc comments
- Include examples in documentation where helpful
- Update README.md if adding new features
- Keep CHANGELOG.md up to date

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for high code coverage
- Test edge cases and error conditions

```bash
npm test
npm run test:coverage
```

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Follow the code standards
   - Add tests for new functionality

3. **Test Your Changes**
   ```bash
   npm run lint
   npm run build
   npm test
   ```

4. **Commit Your Changes**
   ```bash
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions or changes
   - `chore:` - Build process or tooling changes

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub

## Areas for Contribution

### High Priority

- Additional integration types (databases, cloud services)
- Advanced visualization components
- More AI/ML algorithms
- Performance optimizations
- Documentation improvements

### Good First Issues

- Adding more example configurations
- Improving error messages
- Writing additional tests
- Documentation updates
- Bug fixes

## Questions or Issues?

- Open an issue for bugs or feature requests
- Use discussions for questions and ideas
- Tag maintainers for urgent issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Commercial-View! 🎉
