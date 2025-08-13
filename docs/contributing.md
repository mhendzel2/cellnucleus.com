# Contributing to Nuclear Biology Reviews

Thank you for your interest in contributing to the Nuclear Biology Reviews project! This document provides guidelines for contributing to this academic research repository.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Content Guidelines](#content-guidelines)
4. [Technical Contributions](#technical-contributions)
5. [Review Process](#review-process)
6. [Style Guide](#style-guide)
7. [Resources](#resources)

---

## 🤝 Code of Conduct

This project is committed to providing a welcoming environment for all contributors. We expect all participants to:

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the research community
- Show empathy towards other community members

---

## 🚀 How to Contribute

### Types of Contributions

We welcome several types of contributions:

1. **Content Reviews:**
   - New nuclear biology research reviews
   - Updates to existing reviews
   - Fact-checking and accuracy improvements

2. **Technical Improvements:**
   - Website functionality enhancements
   - Performance optimizations
   - Accessibility improvements
   - Bug fixes

3. **Documentation:**
   - Improving this contributing guide
   - Adding deployment instructions
   - Creating user guides

4. **Quality Assurance:**
   - Testing website functionality
   - Link checking
   - Content validation

### Getting Started

1. **Fork the Repository**
   ```bash
   git fork https://github.com/nuclear-biology/reviews.git
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/reviews.git
   cd reviews
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-contribution-name
   ```

4. **Make Your Changes**
   - Follow the style guide
   - Test your changes locally
   - Document your work

5. **Submit a Pull Request**
   - Clear description of changes
   - Reference any related issues
   - Include screenshots if applicable

---

## 📚 Content Guidelines

### Academic Standards

All content must meet academic standards:

- **Accuracy:** Based on peer-reviewed research
- **Citations:** Proper attribution required
- **Objectivity:** Neutral, scientific tone
- **Currency:** Up-to-date information
- **Relevance:** Focus on nuclear biology

### Review Format

New reviews should follow this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>[Title] - Nuclear Biology Reviews</title>
    <meta name="description" content="[Brief description]">
    <link rel="stylesheet" href="../assets/css/styles.css">
</head>
<body>
    <header>
        <!-- Navigation will be added automatically -->
    </header>

    <main>
        <article>
            <h1>[Review Title]</h1>

            <section class="abstract">
                <h2>Abstract</h2>
                <p>[Brief summary of the review]</p>
            </section>

            <section class="introduction">
                <h2>Introduction</h2>
                <!-- Content -->
            </section>

            <!-- Additional sections as needed -->

            <section class="references">
                <h2>References</h2>
                <ol>
                    <!-- Citations -->
                </ol>
            </section>
        </article>
    </main>
</body>
</html>
```

### File Naming Convention

- Use kebab-case: `nuclear-membrane-structure.html`
- Descriptive names: `cellular-division-mechanisms.html`
- No spaces or special characters
- Maximum 50 characters

---

## 🔧 Technical Contributions

### Development Environment

1. **Prerequisites:**
   - Git
   - Modern web browser
   - Text editor/IDE
   - Python or Node.js (for local server)

2. **Setup:**
   ```bash
   npm install
   npm start
   ```

3. **Testing:**
   ```bash
   npm run validate  # HTML validation
   npm run lint-css  # CSS linting
   npm run lint-js   # JavaScript linting
   ```

### Code Standards

- **HTML:** Valid HTML5, semantic markup
- **CSS:** BEM methodology, responsive design
- **JavaScript:** ES6+, documented functions
- **Accessibility:** WCAG 2.1 AA compliance

### Performance Requirements

- Page load time < 3 seconds
- Lighthouse score > 90
- Mobile-friendly design
- SEO optimized

---

## 🔍 Review Process

### Content Review

1. **Academic Review:**
   - Expert verification of scientific accuracy
   - Citation verification
   - Peer review process

2. **Editorial Review:**
   - Grammar and style check
   - Formatting consistency
   - Readability assessment

### Technical Review

1. **Code Review:**
   - Functionality testing
   - Performance impact
   - Security considerations
   - Browser compatibility

2. **Quality Assurance:**
   - Automated testing
   - Manual testing
   - Accessibility audit

### Approval Process

1. **Initial Submission:** Pull request created
2. **Automated Checks:** CI/CD pipeline runs
3. **Peer Review:** Community feedback
4. **Maintainer Review:** Final approval
5. **Merge:** Integration into main branch

---

## 📝 Style Guide

### Writing Style

- **Tone:** Professional, academic
- **Voice:** Third person, objective
- **Tense:** Present for current facts, past for studies
- **Citations:** APA format preferred

### Technical Style

- **HTML:** 2-space indentation, semantic tags
- **CSS:** Mobile-first, BEM naming
- **JavaScript:** camelCase, JSDoc comments
- **File Organization:** Logical directory structure

### Commit Messages

```
feat: add new review on mitochondrial dynamics
fix: correct citation format in nuclear pore review
docs: update contributing guidelines
style: improve mobile responsiveness
refactor: optimize search functionality
test: add validation for review links
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New review content
- [ ] Bug fix
- [ ] Feature enhancement
- [ ] Documentation update

## Testing
- [ ] Local testing completed
- [ ] Links verified
- [ ] Mobile responsiveness checked

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## 📖 Resources

### Academic Resources

- [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
- [Nature Cell Biology](https://www.nature.com/ncb/)
- [Journal of Cell Biology](https://rupress.org/jcb)
- [Cell](https://www.cell.com/)

### Technical Resources

- [MDN Web Docs](https://developer.mozilla.org/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [GitHub Docs](https://docs.github.com/)
- [Jekyll Documentation](https://jekyllrb.com/docs/)

### Tools

- [HTML Validator](https://validator.w3.org/)
- [CSS Validator](https://jigsaw.w3.org/css-validator/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WAVE Accessibility Checker](https://wave.webaim.org/)

---

## ❓ Questions?

If you have questions about contributing:

1. **Check existing issues:** Look for similar questions
2. **Read documentation:** Review this guide and README
3. **Ask the community:** Open a discussion issue
4. **Contact maintainers:** Direct message for sensitive topics

---

## 🏆 Recognition

Contributors will be recognized through:

- **Contributors list:** README acknowledgment
- **Commit history:** Permanent project record
- **Academic citations:** Where appropriate
- **Community highlights:** Featured contributions

---

**Thank you for contributing to nuclear biology research!**

*Last Updated: 2024*
*Version: 1.0.0*