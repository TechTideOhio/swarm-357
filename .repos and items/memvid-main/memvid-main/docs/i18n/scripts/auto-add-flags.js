const fs = require('fs');
const path = require('path');

const I18N_DIR = path.join(__dirname, '..');
const ROOT_DIR = path.join(I18N_DIR, '..', '..');
const README_PATH = path.join(ROOT_DIR, 'README.md');

const LANG_MAP = {
    'aa': { emoji: '🌐', name: 'Afar' },
    'ab': { emoji: '🌐', name: 'Abkhazian' },
    'ae': { emoji: '🌐', name: 'Avestan' },
    'af': { emoji: '🇿🇦', name: 'Afrikaans' },
    'ak': { emoji: '🌐', name: 'Akan' },
    'am': { emoji: '🇪🇹', name: 'Amharic' },
    'an': { emoji: '🌐', name: 'Aragonese' },
    'ar': { emoji: '🇸🇦', name: 'العربية' },
    'as': { emoji: '🌐', name: 'Assamese' },
    'av': { emoji: '🌐', name: 'Avaric' },
    'ay': { emoji: '🌐', name: 'Aymara' },
    'az': { emoji: '🇦🇿', name: 'Azerbaijani' },
    'ba': { emoji: '🌐', name: 'Bashkir' },
    'be': { emoji: '🇧🇾', name: 'Belarusian' },
    'bg': { emoji: '🇧🇬', name: 'Bulgarian' },
    'bi': { emoji: '🌐', name: 'Bislama' },
    'bm': { emoji: '🌐', name: 'Bambara' },
    'bn': { emoji: '🇧🇩', name: 'বাংলা' },
    'bo': { emoji: '🌐', name: 'Tibetan' },
    'br': { emoji: '🌐', name: 'Breton' },
    'bs': { emoji: '🇧🇦', name: 'Bosnian' },
    'ca': { emoji: '🇪🇸', name: 'Catalan' },
    'ce': { emoji: '🌐', name: 'Chechen' },
    'ch': { emoji: '🌐', name: 'Chamorro' },
    'co': { emoji: '🌐', name: 'Corsican' },
    'cr': { emoji: '🌐', name: 'Cree' },
    'cs': { emoji: '🇨🇿', name: 'Česko' },
    'cu': { emoji: '🌐', name: 'Church Slavonic' },
    'cv': { emoji: '🌐', name: 'Chuvash' },
    'cy': { emoji: '🇬🇧', name: 'Welsh' },
    'da': { emoji: '🇩🇰', name: 'Danish' },
    'de': { emoji: '🇩🇪', name: 'Deutsch' },
    'dv': { emoji: '🌐', name: 'Divehi' },
    'dz': { emoji: '🇧🇹', name: 'Dzongkha' },
    'ee': { emoji: '🌐', name: 'Ewe' },
    'el': { emoji: '🇬🇷', name: 'Greek' },
    'en': { emoji: '🇺🇸', name: 'English' },
    'eo': { emoji: '🌐', name: 'Esperanto' },
    'es': { emoji: '🇪🇸', name: 'Español' },
    'et': { emoji: '🇪🇪', name: 'Estonian' },
    'eu': { emoji: '🌐', name: 'Basque' },
    'fa': { emoji: '🇮🇷', name: 'Persian' },
    'ff': { emoji: '🌐', name: 'Fulah' },
    'fi': { emoji: '🇫🇮', name: 'Finnish' },
    'fj': { emoji: '🌐', name: 'Fijian' },
    'fo': { emoji: '🌐', name: 'Faroese' },
    'fr': { emoji: '🇫🇷', name: 'Français' },
    'fy': { emoji: '🌐', name: 'Western Frisian' },
    'ga': { emoji: '🇮🇪', name: 'Irish' },
    'gd': { emoji: '🌐', name: 'Gaelic' },
    'gl': { emoji: '🌐', name: 'Galician' },
    'gn': { emoji: '🌐', name: 'Guarani' },
    'gu': { emoji: '🌐', name: 'Gujarati' },
    'gv': { emoji: '🌐', name: 'Manx' },
    'ha': { emoji: '🇳🇬', name: 'Hausa' },
    'he': { emoji: '🇮🇱', name: 'Hebrew' },
    'hi': { emoji: '🇮🇳', name: 'हिन्दी' },
    'ho': { emoji: '🌐', name: 'Hiri Motu' },
    'hr': { emoji: '🇭🇷', name: 'Croatian' },
    'ht': { emoji: '🌐', name: 'Haitian' },
    'hu': { emoji: '🇭🇺', name: 'Hungarian' },
    'hy': { emoji: '🇦🇲', name: 'Armenian' },
    'hz': { emoji: '🌐', name: 'Herero' },
    'ia': { emoji: '🌐', name: 'Interlingua' },
    'id': { emoji: '🇮🇩', name: 'Bahasa' },
    'ie': { emoji: '🌐', name: 'Interlingue' },
    'ig': { emoji: '🇳🇬', name: 'Igbo' },
    'ii': { emoji: '🌐', name: 'Sichuan Yi' },
    'ik': { emoji: '🌐', name: 'Inupiaq' },
    'io': { emoji: '🌐', name: 'Ido' },
    'is': { emoji: '🇮🇸', name: 'Icelandic' },
    'it': { emoji: '🇮🇹', name: 'Italiano' },
    'iu': { emoji: '🌐', name: 'Inuktitut' },
    'ja': { emoji: '🇯🇵', name: '日本語' },
    'jv': { emoji: '🌐', name: 'Javanese' },
    'ka': { emoji: '🇬🇪', name: 'Georgian' },
    'kg': { emoji: '🌐', name: 'Kongo' },
    'ki': { emoji: '🌐', name: 'Kikuyu' },
    'kj': { emoji: '🌐', name: 'Kuanyama' },
    'kk': { emoji: '🇰🇿', name: 'Kazakh' },
    'kl': { emoji: '🌐', name: 'Kalaallisut' },
    'km': { emoji: '🇰🇭', name: 'Central Khmer' },
    'kn': { emoji: '🌐', name: 'Kannada' },
    'ko': { emoji: '🇰🇷', name: '한국어' },
    'kr': { emoji: '🌐', name: 'Kanuri' },
    'ks': { emoji: '🌐', name: 'Kashmiri' },
    'ku': { emoji: '🇮🇶', name: 'Kurdish' },
    'kv': { emoji: '🌐', name: 'Komi' },
    'kw': { emoji: '🌐', name: 'Cornish' },
    'ky': { emoji: '🇰🇬', name: 'Kyrgyz' },
    'la': { emoji: '🌐', name: 'Latin' },
    'lb': { emoji: '🌐', name: 'Luxembourgish' },
    'lg': { emoji: '🌐', name: 'Ganda' },
    'li': { emoji: '🌐', name: 'Limburgan' },
    'ln': { emoji: '🌐', name: 'Lingala' },
    'lo': { emoji: '🇱🇦', name: 'Lao' },
    'lt': { emoji: '🇱🇹', name: 'Lithuanian' },
    'lu': { emoji: '🌐', name: 'Luba-Katanga' },
    'lv': { emoji: '🇱🇻', name: 'Latvian' },
    'mg': { emoji: '🌐', name: 'Malagasy' },
    'mh': { emoji: '🌐', name: 'Marshallese' },
    'mi': { emoji: '🌐', name: 'Maori' },
    'mk': { emoji: '🇲🇰', name: 'Macedonian' },
    'ml': { emoji: '🌐', name: 'Malayalam' },
    'mn': { emoji: '🇲🇳', name: 'Mongolian' },
    'mr': { emoji: '🌐', name: 'Marathi' },
    'ms': { emoji: '🇲🇾', name: 'Malay' },
    'mt': { emoji: '🇲🇹', name: 'Maltese' },
    'my': { emoji: '🇲🇲', name: 'Burmese' },
    'na': { emoji: '🌐', name: 'Nauru' },
    'nb': { emoji: '🌐', name: 'Norwegian Bokmål' },
    'nd': { emoji: '🌐', name: 'North Ndebele' },
    'ne': { emoji: '🇳🇵', name: 'Nepali' },
    'ng': { emoji: '🌐', name: 'Ndonga' },
    'nl': { emoji: '🇧🇪/🇳🇱', name: 'Nederlands' },
    'nn': { emoji: '🌐', name: 'Norwegian Nynorsk' },
    'no': { emoji: '🇳🇴', name: 'Norwegian' },
    'nr': { emoji: '🌐', name: 'South Ndebele' },
    'nv': { emoji: '🌐', name: 'Navajo' },
    'ny': { emoji: '🌐', name: 'Chichewa' },
    'oc': { emoji: '🌐', name: 'Occitan' },
    'oj': { emoji: '🌐', name: 'Ojibwa' },
    'om': { emoji: '🌐', name: 'Oromo' },
    'or': { emoji: '🌐', name: 'Oriya' },
    'os': { emoji: '🌐', name: 'Ossetian' },
    'pa': { emoji: '🌐', name: 'Punjabi' },
    'pi': { emoji: '🌐', name: 'Pali' },
    'pl': { emoji: '🇵��', name: 'Polski' },
    'ps': { emoji: '🇦🇫', name: 'Pashto' },
    'pt': { emoji: '🇵🇹', name: 'Português' },
    'qu': { emoji: '🌐', name: 'Quechua' },
    'rm': { emoji: '🌐', name: 'Romansh' },
    'rn': { emoji: '🌐', name: 'Rundi' },
    'ro': { emoji: '🇷🇴', name: 'Romanian' },
    'ru': { emoji: '🇷🇺', name: 'Русский' },
    'rw': { emoji: '🌐', name: 'Kinyarwanda' },
    'sa': { emoji: '🌐', name: 'Sanskrit' },
    'sc': { emoji: '🌐', name: 'Sardinian' },
    'sd': { emoji: '🌐', name: 'Sindhi' },
    'se': { emoji: '🌐', name: 'Northern Sami' },
    'sg': { emoji: '🌐', name: 'Sango' },
    'si': { emoji: '🇱🇰', name: 'Sinhala' },
    'sk': { emoji: '🇸🇰', name: 'Slovak' },
    'sl': { emoji: '🇸🇮', name: 'Slovenian' },
    'sm': { emoji: '🌐', name: 'Samoan' },
    'sn': { emoji: '🌐', name: 'Shona' },
    'so': { emoji: '🇸🇴', name: 'Soomaali' },
    'sq': { emoji: '🇦🇱', name: 'Albanian' },
    'sr': { emoji: '🇷🇸', name: 'Serbian' },
    'ss': { emoji: '🌐', name: 'Swati' },
    'st': { emoji: '🇿🇦', name: 'Southern Sotho' },
    'su': { emoji: '🌐', name: 'Sundanese' },
    'sv': { emoji: '🇸🇪', name: 'Swedish' },
    'sw': { emoji: '🇰🇪', name: 'Swahili' },
    'ta': { emoji: '🌐', name: 'Tamil' },
    'te': { emoji: '🌐', name: 'Telugu' },
    'tg': { emoji: '🇹🇯', name: 'Tajik' },
    'th': { emoji: '🇹🇭', name: 'Thai' },
    'ti': { emoji: '🌐', name: 'Tigrinya' },
    'tk': { emoji: '🇹🇲', name: 'Turkmen' },
    'tl': { emoji: '🇵🇭', name: 'Tagalog' },
    'tn': { emoji: '🌐', name: 'Tswana' },
    'to': { emoji: '🌐', name: 'Tonga' },
    'tr': { emoji: '🇹🇷', name: 'Türkçe' },
    'ts': { emoji: '🌐', name: 'Tsonga' },
    'tt': { emoji: '🌐', name: 'Tatar' },
    'tw': { emoji: '🌐', name: 'Twi' },
    'ty': { emoji: '🌐', name: 'Tahitian' },
    'ug': { emoji: '🌐', name: 'Uighur' },
    'uk': { emoji: '🇺🇦', name: 'Ukrainian' },
    'ur': { emoji: '🇵🇰', name: 'Urdu' },
    'uz': { emoji: '🇺🇿', name: 'Uzbek' },
    've': { emoji: '🌐', name: 'Venda' },
    'vi': { emoji: '🇻🇳', name: 'Tiếng Việt' },
    'vo': { emoji: '🌐', name: 'Volapük' },
    'wa': { emoji: '🌐', name: 'Walloon' },
    'wo': { emoji: '🌐', name: 'Wolof' },
    'xh': { emoji: '🇿🇦', name: 'Xhosa' },
    'yi': { emoji: '🌐', name: 'Yiddish' },
    'yo': { emoji: '🇳🇬', name: 'Yoruba' },
    'za': { emoji: '🌐', name: 'Zhuang' },
    'zh': { emoji: '🇨🇳', name: '中文' },
    'zh-CN': { emoji: '🇨🇳', name: '中文 (简体)' },
    'zh-HK': { emoji: '🇭🇰', name: '中文 (繁體)' },
    'zh-Hans': { emoji: '🇨🇳', name: '中文 (简体)' },
    'zh-Hant': { emoji: '🇹🇼', name: '中文 (繁體)' },
    'zh-MO': { emoji: '🇲🇴', name: '中文 (繁體)' },
    'zh-SG': { emoji: '🇸🇬', name: '中文 (繁體)' },
    'zh-TW': { emoji: '🇹🇼', name: '中文 (繁體)' },
    'zu': { emoji: '🇿🇦', name: 'Zulu' },
};

function autoAddFlags() {
    if (!fs.existsSync(README_PATH)) {
        console.error('Error: Cannot find ' + README_PATH);
        process.exit(1);
    }

    let readmeContent = fs.readFileSync(README_PATH, 'utf-8');
    const marker = ' <!-- Next Flag -->';

    if (!readmeContent.includes(marker)) {
        console.warn('Error: <!-- Next Flag --> marker not found in ' + README_PATH);
        console.warn('Please add the marker where you want new flags to be inserted.');
        return;
    }

    const files = fs.readdirSync(I18N_DIR);

    const translationFiles = files.filter(f =>
        f.startsWith('README') &&
        f.endsWith('.md') &&
        f !== 'README.md'
    );

    let updated = false;

    translationFiles.forEach(file => {
        const code = file.split('.')[1];
        const lang = LANG_MAP[code];

        if (!lang) return;

        const flagLink = ` <a href="docs/i18n/${file}">${lang.emoji} ${lang.name}</a>`;

        if (!readmeContent.includes(file)) {
            readmeContent = readmeContent.replace(marker, flagLink + '\n' + marker);
            updated = true;
            console.log('Added ' + code);
        }
    });

    if (updated) {
        fs.writeFileSync(README_PATH, readmeContent, 'utf-8');
        console.log('Main README updated.');
    } else {
        console.log('No new flags to add.');
    }
}

autoAddFlags();
