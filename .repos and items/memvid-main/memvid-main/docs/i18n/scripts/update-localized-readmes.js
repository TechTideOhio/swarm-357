const fs = require('fs');
const path = require('path');

const I18N_DIR = path.join(__dirname, '..');
const ROOT_DIR = path.join(I18N_DIR, '..', '..');
const README_PATH = path.join(ROOT_DIR, 'README.md');

const MARKERS = {
    HEADER: {
        START: '<!-- HEADER:START -->',
        END: '<!-- HEADER:END -->'
    },
    FLAGS: {
        START: '<!-- FLAGS:START -->',
        END: '<!-- FLAGS:END -->'
    },
    NAV: {
        START: '<!-- NAV:START -->',
        END: '<!-- NAV:END -->'
    },
    BADGES: {
        START: '<!-- BADGES:START -->',
        END: '<!-- BADGES:END -->'
    }
};

function extractBlock(content, marker) {
    const startIdx = content.indexOf(marker.START);
    const endIdx = content.indexOf(marker.END);

    if (startIdx === -1 || endIdx === -1) {
        return null;
    }

    return content.substring(startIdx, endIdx + marker.END.length);
}

function updateOrInsertBlock(targetContent, blockKey, blockValue, fallbackAnchor = null) {
    const marker = MARKERS[blockKey];
    const startIdx = targetContent.indexOf(marker.START);
    const endIdx = targetContent.indexOf(marker.END);

    if (startIdx !== -1 && endIdx !== -1) {
        const prefix = targetContent.substring(0, startIdx);
        const suffix = targetContent.substring(endIdx + marker.END.length);
        return prefix + blockValue + suffix;
    }

    if (startIdx !== -1 || endIdx !== -1) {
        let cleaned = targetContent.split(marker.START).join('');
        cleaned = cleaned.split(marker.END).join('');
        return updateOrInsertBlock(cleaned, blockKey, blockValue, fallbackAnchor);
    }

    if (fallbackAnchor) {
        const anchorIdx = targetContent.indexOf(fallbackAnchor);
        if (anchorIdx !== -1) {
            const insertAfterIdx = targetContent.indexOf('\n', anchorIdx) + 1;
            const prefix = targetContent.substring(0, insertAfterIdx);
            const suffix = targetContent.substring(insertAfterIdx);
            return prefix + '\n' + blockValue + '\n' + suffix;
        }
    }

    return targetContent + '\n\n' + blockValue;
}

function updateLocalizedReadmes() {
    if (!fs.existsSync(README_PATH)) {
        console.error('Error: Cannot find ' + README_PATH);
        process.exit(1);
    }

    const readmeContent = fs.readFileSync(README_PATH, 'utf-8');

    const headerBlock = extractBlock(readmeContent, MARKERS.HEADER);
    const flagsBlock = extractBlock(readmeContent, MARKERS.FLAGS);
    const navBlock = extractBlock(readmeContent, MARKERS.NAV);
    const badgesBlock = extractBlock(readmeContent, MARKERS.BADGES);

    if (!headerBlock || !flagsBlock || !navBlock || !badgesBlock) {
        console.error('Error: Some markers are missing in main README.md');
        if (!headerBlock) console.error('Missing: HEADER');
        if (!flagsBlock) console.error('Missing: FLAGS');
        if (!navBlock) console.error('Missing: NAV');
        if (!badgesBlock) console.error('Missing: BADGES');
        process.exit(1);
    }

    let flagsI18n = flagsBlock.split('href="docs/i18n/').join('href="');
    flagsI18n = flagsI18n.split('href="README.md"').join('href="../../README.md"');

    const files = fs.readdirSync(I18N_DIR);
    const targetFiles = files
        .filter(file => file.startsWith('README.') && file.endsWith('.md') && file !== 'README.md')
        .map(file => path.join(I18N_DIR, file));

    targetFiles.forEach(filePath => {
        let content = fs.readFileSync(filePath, 'utf-8');
        const fileName = path.basename(filePath);

        content = updateOrInsertBlock(content, 'HEADER', headerBlock, '<img');
        content = updateOrInsertBlock(content, 'FLAGS', flagsI18n, MARKERS.HEADER.END);
        content = updateOrInsertBlock(content, 'NAV', navBlock, MARKERS.FLAGS.END);
        content = updateOrInsertBlock(content, 'BADGES', badgesBlock, MARKERS.NAV.END);

        fs.writeFileSync(filePath, content, 'utf-8');
        console.log('Updated ' + fileName);
    });

    console.log('\nSuccess: Done.');
}

updateLocalizedReadmes();
