# Internationalization (i18n) - README Translations

This folder contains translated versions of the main [README.md](../../README.md) file for different languages.

## Purpose

The `docs/i18n/` directory is dedicated to making Memvid accessible to developers worldwide by providing localized versions of the main README. Each translation helps non-English speakers understand and use Memvid more effectively.

## Structure

```
docs/i18n/
├── README.md          # This file
├── README.zh-CN.md    # Chinese (Simplified) translation
├── README.zh-TW.md    # Chinese (Traditional) translation
├── README.es.md       # Spanish translation
├── README.fr.md       # French translation
├── README.de.md       # German translation
├── README.ja.md       # Japanese translation
├── README.ko.md       # Korean translation
├── README.pt-BR.md    # Portuguese (Brazil) translation
├── README.so.md       # Somali translation
└── ...                # Additional languages
```

## Contributing Translations

We welcome contributions of README translations! For detailed guidelines, see [Contributing Translations](CONTRIBUTING_TRANSLATIONS.md).

Here's a quick overview:

### 1. Check Existing Translations

Before starting, check if a translation for your language already exists or is in progress.

### 2. Create a Translation File

- Use the format: `README.{language-code}.md`
- Use standard language codes (e.g., `zh-CN`, `es`, `fr`, `de`, `ja`, `ko`, `pt-BR`, `so`)
- Copy the main `README.md` as a starting point

### 3. Translation Guidelines

- **Keep the structure**: Maintain the same headings, sections, and formatting as the original
- **Preserve links**: Keep all URLs and links unchanged
- **Preserve code blocks**: Keep code examples, commands, and technical terms in English (or add comments in the target language)
- **Update badges**: Keep badges and shields as they are (they're language-agnostic)
- **Maintain accuracy**: Ensure technical accuracy while making the content natural in the target language

### 4. Submit Your Translation

1. Create a new file: `README.{language-code}.md` in this directory
2. Translate the content while following the guidelines above
3. Submit a pull request with:
   - A clear description of the language being added
   - Your name/username for attribution (if desired)

## Language Codes

Use standard ISO 639-1 or ISO 639-2 language codes:

- `zh-CN` - Chinese (Simplified)
- `zh-TW` - Chinese (Traditional)
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `ko` - Korean
- `pt-BR` - Portuguese (Brazil)
- `ru` - Russian
- `ar` - Arabic
- `hi` - Hindi
- `so` - Somali
- And more...

## Maintenance

Translations should be updated when the main README is significantly changed. Contributors are encouraged to keep their translations in sync with the English version.

## Questions?

If you have questions about translations or want to coordinate with other translators, please:
- See [Contributing Translations](CONTRIBUTING_TRANSLATIONS.md) for detailed guidelines
- Open an issue on GitHub
- Join our [Discussions](https://github.com/memvid/memvid/discussions)
- Contact: contact@memvid.com

---

**Thank you for helping make Memvid accessible to developers worldwide! 🌍**
