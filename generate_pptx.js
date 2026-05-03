// generate_pptx.js - PPT generator using PptxGenJS
// All Chinese strings use \uXXXX escapes to avoid file encoding issues on Windows
'use strict';

const PptxGen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

function main() {
  let input = process.argv[2];
  if (!input) {
    // Read from stdin with explicit UTF-8 encoding
    process.stdin.setEncoding('utf8');
    const chunks = [];
    process.stdin.on('data', chunk => chunks.push(chunk));
    process.stdin.on('end', () => {
      input = chunks.join('');
      try {
        const data = JSON.parse(input);
        const { title, content, themeName } = data;
        generatePptx(title, content, themeName || '\u9ed8\u8ba4')
          .then(buf => process.stdout.write(buf.toString('base64')))
          .catch(err => {
            process.stderr.write('Error: ' + err.message + '\n');
            process.exit(1);
          });
      } catch (e) {
        process.stderr.write('Invalid JSON: ' + e.message + '\n');
        process.exit(1);
      }
    });
    return;
  }

  // If argument starts with @, read from file
  if (input.startsWith('@')) {
    const filePath = input.substring(1);
    try {
      input = fs.readFileSync(filePath, 'utf8');
    } catch (e) {
      process.stderr.write('Cannot read file: ' + filePath + '\n');
      process.exit(1);
    }
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch (e) {
    process.stderr.write('Invalid JSON: ' + e.message + '\n');
    process.exit(1);
  }
  const { title, content, themeName } = data;
  generatePptx(title, content, themeName || '\u9ed8\u8ba4')
    .then(buf => process.stdout.write(buf.toString('base64')))
    .catch(err => {
      process.stderr.write('Error: ' + err.message + '\n');
      process.exit(1);
    });
}

async function generatePptx(title, content, themeName) {
  const pages = parseContent(content);
  process.stderr.write('DEBUG: parsed ' + pages.length + ' pages\n');
  pages.forEach((p, i) => {
    process.stderr.write('  page ' + (i+1) + ': type=' + p.type + ' title=' + p.title + '\n');
  });

  const pres = new PptxGen();
  pres.layout = 'LAYOUT_16x9';
  pres.title = title;
  pres.author = 'SlideCraft';

  const theme = getTheme(themeName);

  pages.forEach((page, i) => {
    const slide = pres.addSlide();
    const pageNum = i + 1;
    switch (page.type) {
      case 'cover':
        renderCover(slide, page, theme);
        break;
      case 'toc':
        renderToc(slide, page, theme, pageNum);
        break;
      case 'content':
        renderContent(slide, page, theme, pageNum);
        break;
      case 'summary':
        renderSummary(slide, page, theme, pageNum);
        break;
      default:
        renderContent(slide, page, theme, pageNum);
    }
  });

  const tmpFile = path.join(__dirname, 'tmp_' + Date.now() + '.pptx');
  await pres.writeFile({ fileName: tmpFile });
  const buffer = fs.readFileSync(tmpFile);
  fs.unlinkSync(tmpFile);
  return buffer;
}

function getTheme(name) {
  const themes = {
    // \u9ed8\u8ba4 = 默认
    '\u9ed8\u8ba4': { primary: '1A3A6F', secondary: '2D5A2D', accent: '4A7C4A', light: '8FBC8F', bg: 'FFFFFF' },
    // \u68ee\u6797\u58a8 = 森林墨
    '\u68ee\u6797\u58a8': { primary: '1A3A6F', secondary: '2D5A2D', accent: '4A7C4A', light: '8FBC8F', bg: 'F0F8F0' },
    // \u79d1\u6280\u84dd = 科技蓝
    '\u79d1\u6280\u84dd': { primary: '1E3A5F', secondary: '2E5A8F', accent: '4A90D9', light: 'A8D4FF', bg: 'F0F5FF' },
    // \u6a31\u7c89 = 樱粉
    '\u6a31\u7c89': { primary: '8B3A62', secondary: 'D4708A', accent: 'E8A0B0', light: 'F5D0D8', bg: 'FFF5F7' },
    // \u661f\u7a7a\u84dd = 星空蓝
    '\u661f\u7a7a\u84dd': { primary: '1A1A2E', secondary: '16213E', accent: '0F3460', light: '4A90D9', bg: 'F0F4FF' },
  };
  return themes[name] || themes['\u9ed8\u8ba4'];
}

function renderCover(slide, page, theme) {
  slide.background = { color: theme.primary };
  if (page.title) {
    slide.addText(page.title, {
      x: 0.6, y: 1.8, w: 8.8, h: 1.5,
      fontSize: 44, fontFace: 'Microsoft YaHei',
      color: 'FFFFFF', bold: true, align: 'left', fit: 'shrink'
    });
  }
  if (page.subtitle) {
    slide.addText(page.subtitle, {
      x: 0.6, y: 3.5, w: 8.0, h: 0.6,
      fontSize: 18, fontFace: 'Microsoft YaHei',
      color: theme.light, align: 'left'
    });
  }
}

function renderToc(slide, page, theme, pageNum) {
  slide.background = { color: theme.bg };
  // \u76ee\u5f55 = 目录
  slide.addText('\u76ee\u5f55', {
    x: 0.5, y: 0.4, w: 9, h: 0.7,
    fontSize: 32, fontFace: 'Microsoft YaHei',
    color: theme.primary, bold: true
  });
  const items = (page.items && page.items.length > 0) ? page.items : page.bullets;
  if (items && items.length > 0) {
    items.forEach((item, idx) => {
      const y = 1.5 + idx * 0.8;
      slide.addText((idx + 1) + '. ' + item, {
        x: 0.8, y: y, w: 8, h: 0.6,
        fontSize: 18, fontFace: 'Microsoft YaHei',
        color: theme.secondary
      });
    });
  }
  addPageNum(slide, pageNum, theme);
}

function renderContent(slide, page, theme, pageNum) {
  slide.background = { color: theme.bg };
  if (page.title) {
    slide.addText(page.title, {
      x: 0.5, y: 0.4, w: 8.5, h: 0.6,
      fontSize: 26, fontFace: 'Microsoft YaHei',
      color: theme.primary, bold: true, fit: 'shrink'
    });
  }
  const bullets = (page.bullets && page.bullets.length > 0) ? page.bullets : page.items;
  if (bullets && bullets.length > 0) {
    bullets.forEach((b, idx) => {
      const y = 1.5 + idx * 0.7;
      slide.addText('\u25cf ' + b, {
        x: 0.8, y: y, w: 8.5, h: 0.6,
        fontSize: 16, fontFace: 'Microsoft YaHei',
        color: theme.secondary
      });
    });
  }
  addPageNum(slide, pageNum, theme);
}

function renderSummary(slide, page, theme, pageNum) {
  slide.background = { color: theme.primary };
  // \u8c22\u8c22 = 谢谢
  const titleText = page.title || '\u8c22\u8c22';
  slide.addText(titleText, {
    x: 0.5, y: 2.0, w: 9, h: 1.2,
    fontSize: 48, fontFace: 'Microsoft YaHei',
    color: 'FFFFFF', bold: true, align: 'center'
  });
  if (page.subtitle) {
    slide.addText(page.subtitle, {
      x: 0.5, y: 3.5, w: 9, h: 0.6,
      fontSize: 18, fontFace: 'Microsoft YaHei',
      color: theme.light, align: 'center'
    });
  }
  addPageNum(slide, pageNum, theme);
}

function addPageNum(slide, pageNum, theme) {
  slide.addText(String(pageNum), {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fontSize: 11, fontFace: 'Arial',
    color: 'FFFFFF', bold: true,
    align: 'center', valign: 'middle',
    fill: { color: theme.accent }
  });
}

/**
 * Clean markdown formatting from a string.
 * All Chinese chars use \uXXXX to avoid file encoding issues.
 */
function cleanMarkdown(s) {
  if (!s) return '';
  // Remove markdown heading markers
  s = s.replace(/^#{1,6}\s+/, '');
  // Remove horizontal rules
  s = s.replace(/^-{3,}\s*$/gm, '');
  // Remove bold markers
  s = s.replace(/\*\*(.+?)\*\*/g, '$1');
  // Remove list markers
  s = s.replace(/^[\*\-]\s+/, '');
  s = s.replace(/^\d+[.\u3001]\s+/, '');
  // Remove \u8981\u70b9[\uff1a:] prefix (\u8981\u70b9 = 要点)
  s = s.replace(/^\u8981\u70b9[\uff1a:]\s*/, '');
  // Remove \u3010\u3011 brackets at start/end
  s = s.replace(/^[\u3010\u3011]+/, '');
  s = s.replace(/[\u3010\u3011]+$/, '');
  // Deduplicate \u7b2c character (\u7b2c = 第)
  s = s.replace(/\u7b2c+/g, '\u7b2c');
  return s.trim();
}

/**
 * Parse AI-generated outline text into page objects.
 * Supports formats:
 *   \u30101\u9875\uff1a\u5c01\u9762\u3011  (\u30101 = 【, \u9875 = 页, \uff1a = ：, \u5c01\u9762 = 封面, \u3011 = 】)
 *   \u6700\u540e1\u9875\uff1a\u7ed3\u675f\u9875\u3011 (\u6700\u540e = 最后, \u7ed3\u675f\u9875 = 结束页)
 */
function parseContent(content) {
  const pages = [];
  const lines = content.split('\n');
  let currentPage = null;
  let currentType = null;
  let collecting = [];

  function savePage() {
    if (currentPage) {
      if (collecting.length > 0) {
        if (!currentPage.bullets) currentPage.bullets = [];
        collecting.forEach(function(line) {
          const cleaned = cleanMarkdown(line);
          if (cleaned && cleaned.length > 1) {
            currentPage.bullets.push(cleaned);
          }
        });
      }
      pages.push(currentPage);
      currentPage = null;
      currentType = null;
      collecting = [];
    }
  }

  // Regex patterns using Unicode escapes:
  // \u3010 = 【, \u3011 = 】, \u7b2c = 第, \u9875 = 页, \uff1a = ：
  // \u6700\u540e = 最后
  const RE_PAGE = /^\u3010?(?:\u7b2c\s*(\d+)\s*\u9875|\u6700\u540e\s*\d*\s*\u9875)[\uff1a:\s]+([^\u3010\u3011\n]+)\u3011?/;
  const RE_PAGE2 = /^\u3010?\u7b2c?\s*(\d+)\s*\u9875[\uff1a:\s]+([^\u3010\u3011\n]+)\u3011?/;

  // Keywords (Unicode escaped)
  const KW_COVER = '\u5c01\u9762';      // 封面
  const KW_TOC = '\u76ee\u5f55';        // 目录
  const KW_END1 = '\u7ed3\u675f';       // 结束
  const KW_END2 = '\u8c22\u8c22';       // 谢谢
  const KW_SUBTITLE = '\u526f\u6807\u9898'; // 副标题
  const KW_TITLE = '\u6807\u9898';      // 标题
  const KW_BULLET = '\u8981\u70b9';     // 要点
  const KW_TOC_NUM = /^\d+[.\uff0e\u3001\uff1a:]\s*(.+)/; // 1. or 1。 etc.

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Detect page header
    const pageMatch = trimmed.match(RE_PAGE) || trimmed.match(RE_PAGE2);
    if (pageMatch) {
      savePage();
      // pageMatch[2] = page type label (may be undefined for RE_PAGE2 fallback)
      const pageLabel = (pageMatch[2] || pageMatch[1] || '').toLowerCase().trim();
      currentPage = { type: 'content', title: '', subtitle: '', bullets: [] };

      if (pageLabel.indexOf(KW_COVER) >= 0 || pageLabel.indexOf('cover') >= 0) {
        currentPage.type = 'cover';
      } else if (pageLabel.indexOf(KW_TOC) >= 0 || pageLabel.indexOf('toc') >= 0) {
        currentPage.type = 'toc';
        currentPage.items = [];
      } else if (pageLabel.indexOf(KW_END1) >= 0 || pageLabel.indexOf(KW_END2) >= 0 ||
                 pageLabel.indexOf('end') >= 0 || pageLabel.indexOf('thank') >= 0) {
        currentPage.type = 'summary';
      } else {
        // Content page: extract title from match
        const rawLabel = trimmed.match(/^\u3010?(?:\u7b2c\s*\d+\s*\u9875|\u6700\u540e\s*\d*\s*\u9875)[\uff1a:\s]+([^\u3010\u3011\n]+)/);
        currentPage.title = rawLabel ? rawLabel[1].trim().replace(/\u3011+$/, '') : pageLabel;
      }
      currentType = currentPage.type;
      continue;
    }

    if (!currentPage) {
      // No current page - check if this is start of cover
      if (trimmed.startsWith(KW_SUBTITLE) || trimmed.startsWith(KW_TITLE)) {
        currentPage = { type: 'cover', title: '', subtitle: '', bullets: [] };
        currentType = 'cover';
      } else {
        continue;
      }
    }

    // Parse page content
    if (currentType === 'cover' || currentType === 'summary') {
      if (trimmed.startsWith(KW_SUBTITLE) && /[\uff1a:]/.test(trimmed)) {
        currentPage.subtitle = trimmed.split(/[\uff1a:]/)[1].trim();
      } else if (trimmed.startsWith(KW_TITLE) && /[\uff1a:]/.test(trimmed)) {
        currentPage.title = trimmed.split(/[\uff1a:]/)[1].trim();
      }
    } else if (currentType === 'toc') {
      const m = trimmed.match(KW_TOC_NUM);
      if (m) {
        if (!currentPage.items) currentPage.items = [];
        currentPage.items.push(m[1].trim());
      }
    } else {
      // content page: collect bullets
      collecting.push(trimmed);
    }
  }

  savePage();

  if (pages.length === 0) {
    // \u9ed8\u8ba4 = 默认, PPT is ASCII
    pages.push({ type: 'cover', title: 'PPT', subtitle: '', bullets: [] });
  }

  // Ensure there's a summary/end slide
  if (pages[pages.length - 1].type !== 'summary') {
    pages.push({ type: 'summary', title: '\u8c22\u8c22', subtitle: '', bullets: [] });
  }

  return pages;
}

main();
