# Contributing Translations (i18n)

Thank you for helping translate Memvid’s documentation and make the project accessible to a global audience.

This guide explains how to contribute translations for the main `README.md`.

---

## What Can Be Translated

- The main repository `README.md`
- Translations are stored in `docs/i18n/`
- Each language has a single translation file

---

## Translation Workflow

### 1. Check Existing Issues

Before starting:
- Check open issues to see if your language is already in progress
- If an issue exists, comment on it to indicate you want to work on it
- Only one contributor should work on a language at a time

---

### 2. Create a Translation Issue (If Needed)

If no issue exists for your language, open a new one using this format:

**Title:**
```
README translation: <Language> (<code>)
```

**Labels to apply:**
- `i18n`
- `documentation`
- `help wanted` or `good first issue`

---

### 3. Create the Translation File

1. Copy the main `README.md` from the repository root
2. Create a new file in `docs/i18n/` using this format:

   ```
   README.<language-code>.md
   ```

   **Examples:**
- `README.es.md`
- `README.zh-CN.md`
- `README.pt-BR.md`

Use standard ISO language codes (include region where applicable).

---

## Translation Guidelines

- **Preserve structure**  
  Keep headings, section order, and formatting identical to the original README

- **Preserve links and badges**  
  Do not modify URLs, badges, or shields

- **Preserve code blocks**  
  Keep code examples, commands, flags, and API names in English

- **Maintain technical accuracy**  
  Translate naturally, but do not change meaning or behavior

- **Language quality matters**  
  Native or fluent speakers are strongly preferred

---

## Submitting Your Translation

1. **Create a new branch:**
   ```bash
   git checkout -b docs/i18n-<language-code>
   ```

2. **Add your translation file** under `docs/i18n/`

3. **Commit your changes:**
   ```bash
   git commit -m "docs(i18n): add <Language> README translation"
   ```

4. **Push to your fork** and open a Pull Request

5. **Reference the translation issue** in your PR description

---

## Review Process

- Maintainers may request:
  - Clarifications
  - Formatting fixes
  - Review by another native speaker
- Once approved, the PR will be merged
- The corresponding issue will be closed

---

## Keeping Translations Up to Date

When the main `README.md` changes significantly:

- Existing translations may need updates
- Contributors are encouraged to help keep translations in sync

---

## Getting Help

- Open an issue if you have questions about translations
- Use GitHub Discussions for coordination
- Contact: [contact@memvid.com](mailto:contact@memvid.com)
