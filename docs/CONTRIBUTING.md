# Contributing to Fashion Labs

Thank you for your interest in contributing to Fashion Labs! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Feature Requests](#feature-requests)
- [Bug Reports](#bug-reports)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

---

## Getting Started

### 1. Fork the Repository

Click the "Fork" button on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/fashion-labs.git
cd fashion-labs
```

### 3. Set Up Development Environment

Follow the [SETUP_GUIDE.md](SETUP_GUIDE.md) to set up your local environment.

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests

---

## Development Workflow

### 1. Make Your Changes

Edit the relevant files in your branch.

### 2. Test Your Changes

**Backend:**
```bash
cd FRSCA/api
python -m pytest  # If tests exist
```

**Frontend:**
```bash
cd frsca-frontend
npm test
```

### 3. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

**Commit message format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance

**Examples:**
```
feat: add footwear slot to outfit generation
fix: resolve CORS issue in production
docs: update API documentation for new endpoint
refactor: optimize embedding similarity calculation
```

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template
5. Submit for review

---

## Coding Standards

### Python (Backend)

**Style Guide:** Follow [PEP 8](https://pep8.org/)

**Key Points:**
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter)
- Use type hints where possible
- Write docstrings for functions

**Example:**
```python
def generate_outfit(
    metadata: list,
    embeddings: np.ndarray,
    gender: str,
    season: str,
    occasion: str
) -> dict:
    """
    Generate a complete outfit based on user preferences.
    
    Args:
        metadata: List of item metadata dictionaries
        embeddings: NumPy array of item embeddings
        gender: Gender category (men/women)
        season: Season (winter/summer)
        occasion: Occasion type (casual/formal)
    
    Returns:
        Dictionary containing outfit items by slot
    """
    # Implementation
    pass
```

**Formatting:**
```bash
# Install Black formatter
pip install black

# Format code
black scripts/
```

**Linting:**
```bash
# Install flake8
pip install flake8

# Run linter
flake8 scripts/
```

### JavaScript/React (Frontend)

**Style Guide:** Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

**Key Points:**
- Use 2 spaces for indentation
- Use `const` and `let`, avoid `var`
- Use arrow functions for callbacks
- Use meaningful variable names
- Add comments for complex logic

**Example:**
```javascript
/**
 * Generate outfit based on user preferences
 * @param {string} gender - Gender category
 * @param {string} season - Season
 * @param {string} occasion - Occasion type
 */
const generateOutfit = async (gender, season, occasion) => {
  setIsGenerating(true);
  
  try {
    const response = await fetch(`${API_BASE}/generate-outfit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gender, season, occasion })
    });
    
    const data = await response.json();
    setOutfit(data.outfit);
  } catch (error) {
    console.error('Failed to generate outfit:', error);
  } finally {
    setIsGenerating(false);
  }
};
```

**Formatting:**
```bash
# Install Prettier
npm install --save-dev prettier

# Format code
npx prettier --write src/
```

**Linting:**
```bash
# ESLint is included with Create React App
npm run lint
```

---

## Project Structure Guidelines

### Adding New Features

#### Backend Feature

1. **Create new script** in `FRSCA/scripts/`
2. **Add endpoint** in `FRSCA/api/main.py`
3. **Update rules** if needed in `scripts/rules.py`
4. **Document** in API_DOCUMENTATION.md

**Example: Adding Footwear Slot**

```python
# scripts/slots.py
FOOTWEAR_CATEGORIES = {
    "shoes", "sneakers", "boots", "sandals"
}

# scripts/generate_outfit.py
slots = ["TOP", "BOTTOM", "FOOTWEAR"]
if season == "winter":
    slots.append("OUTERWEAR")
```

#### Frontend Feature

1. **Add state** in `App.js`
2. **Create UI components**
3. **Add API calls**
4. **Update styles** in `index.css`

**Example: Adding Favorites**

```javascript
const [favorites, setFavorites] = useState([]);

const toggleFavorite = (outfitId) => {
  setFavorites(prev => 
    prev.includes(outfitId)
      ? prev.filter(id => id !== outfitId)
      : [...prev, outfitId]
  );
};
```

---

## Testing Guidelines

### Backend Tests

Create tests in `FRSCA/tests/`:

```python
# tests/test_generate_outfit.py
import pytest
from scripts.generate_outfit import generate_outfit

def test_generate_outfit_winter_formal():
    outfit = generate_outfit(
        metadata=mock_metadata,
        embeddings=mock_embeddings,
        image_names=mock_names,
        gender="men",
        season="winter",
        occasion="formal"
    )
    
    assert "TOP" in outfit
    assert "BOTTOM" in outfit
    assert "OUTERWEAR" in outfit
```

### Frontend Tests

Create tests in `frsca-frontend/src/`:

```javascript
// App.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('generates outfit on button click', async () => {
  render(<App />);
  
  const button = screen.getByText('Generate Outfit');
  fireEvent.click(button);
  
  // Assert outfit is displayed
  expect(await screen.findByText('Your Outfit')).toBeInTheDocument();
});
```

---

## Documentation

### Code Documentation

- **Python**: Use docstrings (Google or NumPy style)
- **JavaScript**: Use JSDoc comments
- **Complex logic**: Add inline comments

### Project Documentation

When adding features, update:
- `README.md` - If it affects setup or usage
- `API_DOCUMENTATION.md` - For new endpoints
- `ARCHITECTURE.md` - For architectural changes

---

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Commits follow convention
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How has this been tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
```

---

## Feature Requests

### How to Request a Feature

1. **Check existing issues** to avoid duplicates
2. **Open a new issue** with label `enhancement`
3. **Describe the feature** clearly
4. **Explain the use case**
5. **Provide examples** if possible

**Template:**
```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought about
```

---

## Bug Reports

### How to Report a Bug

1. **Check existing issues** to avoid duplicates
2. **Open a new issue** with label `bug`
3. **Provide details** (see template below)

**Template:**
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen?

**Actual Behavior**
What actually happens?

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Python version: [e.g., 3.9]
- Node version: [e.g., 18.0]
```

---

## Review Process

### What to Expect

1. **Initial Review** - Within 2-3 days
2. **Feedback** - Reviewers may request changes
3. **Iteration** - Make requested changes
4. **Approval** - Once approved, PR will be merged
5. **Recognition** - Contributors will be acknowledged

### Review Criteria

- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Breaking changes

---

## Community

### Getting Help

- **GitHub Discussions** - Ask questions
- **Issues** - Report bugs or request features
- **Pull Requests** - Contribute code

### Recognition

Contributors will be acknowledged in:
- README.md
- Release notes
- GitHub contributors page

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Fashion Labs! 🎉**
