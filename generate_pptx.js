const PptxGen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

function main() {
  const input = process.argv[2];
  if (!input) { console.error('Usage: node generate_pptx.js "<json>"'); process.exit(1); }
  let data;
  try { data = JSON.parse(input); } catch (e) { console.error('Invalid JSON:', e.message); process.exit(1); }
  const { title, content, themeName = '默认' } = data;
  generatePptx(title, content, themeName)
    .then(buf => process.stdout.write(buf.toString('base64')))
    .catch(err => { console.error('Error:', err.message); process.exit(1); });
}

async function generatePptx(title, content, themeName) {
  const cleaned = cleanContent(content);
  const pages = parseContent(cleaned);
  console.error('DEBUG pages:' + JSON.stringify(pages.map(p => ({ t: p.type, ttl: p.title }))));

  const pres = new PptxGen();
  pres.layout = 'LAYOUT_16x9';
  pres.title = title;
  pres.author = 'SlideCraft';

  const themes = {
    '默认':   { primary:'1A3A6F', secondary:'2D5A2D', accent:'4A7C4A', light:'8FBC8F', bg:'FFFFFF' },
    '森林墨': { primary:'1A3A6F', secondary:'2D5A2D', accent:'4A7C4A', light:'8FBC8F', bg:'F0F8F0' },
    '科技蓝': { primary:'1E3A5F', secondary:'2E5A8F', accent:'4A90D9', light:'A8D4FF', bg:'F0F5FF' },
    '樱粉':   { primary:'8B3A62', secondary:'D4708A', accent:'E8A0B0', light:'F5D0D8', bg:'FFF5F7' },
    '星空蓝': { primary:'1A1A2E', secondary:'16213E', accent:'0F3460', light:'4A90D9', bg:'F0F4FF' },
  };
  const theme = themes[themeName] || themes['默认'];

  pages.forEach((page, i) => {
    const slide = pres.addSlide();
    const pageNum = i + 1;
    switch (page.type) {
      case 'cover':  renderCover(slide, page, theme, pres); break;
      case 'toc':    renderToc(slide, page, theme, pageNum, pres); break;
      case 'content': renderContent(slide, page, theme, pageNum, pres); break;
      case 'summary': renderSummary(slide, page, theme, pageNum, pres); break;
      default: renderContent(slide, page, theme, pageNum, pres);
    }
  });

  const tmpFile = path.join(__dirname, `tmp_${Date.now()}.pptx`);
  await pres.writeFile({ fileName: tmpFile });
  const buffer = fs.readFileSync(tmpFile);
  fs.unlinkSync(tmpFile);
  return buffer;
}

function makeShadow() {
  return { type: 'outer', blur: 6, offset: 2, color: '000000', opacity: 0.12 };
}

function renderCover(slide, page, theme, pres) {
  const S = pres.shapes;
  slide.background = { color: theme.primary };
  // 左侧装饰条
  slide.addShape(S.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: 5.625,
    fill: { color: theme.accent },
    line: { type: 'none' }
  });
  // 标题
  if (page.title) {
    slide.addText(page.title, {
      x: 0.6, y: 1.8, w: 8.8, h: 1.5,
      fontSize: 44, fontFace: 'Microsoft YaHei',
      color: 'FFFFFF', bold: true, align: 'left',
      fit: 'shrink'
    });
  }
  // 副标题
  if (page.subtitle) {
    slide.addText(page.subtitle, {
      x: 0.6, y: 3.5, w: 8.0, h: 0.6,
      fontSize: 18, fontFace: 'Microsoft YaHei',
      color: theme.light, align: 'left'
    });
  }
  // 底部装饰线
  slide.addShape(S.RECTANGLE, {
    x: 0.6, y: 3.3, w: 2.0, h: 0.05,
    fill: { color: theme.light },
    line: { type: 'none' }
  });
}

function renderToc(slide, page, theme, pageNum, pres) {
  const S = pres.shapes;
  slide.background = { color: theme.bg };
  // 标题
  slide.addText('目录', {
    x: 0.5, y: 0.4, w: 9, h: 0.7,
    fontSize: 32, fontFace: 'Microsoft YaHei',
    color: theme.primary, bold: true
  });
  // 装饰线
  slide.addShape(S.RECTANGLE, {
    x: 0.5, y: 1.15, w: 1.5, h: 0.05,
    fill: { color: theme.accent },
    line: { type: 'none' }
  });
  const items = page.items.length > 0 ? page.items : page.bullets;
  if (items.length > 0) {
    const cols = items.length <= 3 ? 1 : 2;
    const itemsPerCol = Math.ceil(items.length / cols);
    items.forEach((item, idx) => {
      const col = Math.floor(idx / itemsPerCol);
      const row = idx % itemsPerCol;
      const x = 0.8 + col * 4.8;
      const y = 1.5 + row * 0.85;
      // 编号圆圈
      slide.addShape(S.OVAL, {
        x, y, w: 0.4, h: 0.4,
        fill: { color: theme.primary },
        line: { type: 'none' }
      });
      slide.addText(String(idx + 1), {
        x, y, w: 0.4, h: 0.4,
        fontSize: 14, fontFace: 'Arial',
        color: 'FFFFFF', bold: true,
        align: 'center', valign: 'middle'
      });
      // 文字
      slide.addText(item, {
        x: x + 0.55, y, w: 3.8, h: 0.4,
        fontSize: 16, fontFace: 'Microsoft YaHei',
        color: theme.secondary, valign: 'middle'
      });
    });
  }
  addPageNum(slide, pageNum, theme, pres);
}

function renderContent(slide, page, theme, pageNum, pres) {
  const S = pres.shapes;
  slide.background = { color: theme.bg };
  // 标题
  if (page.title) {
    slide.addText(page.title, {
      x: 0.5, y: 0.4, w: 8.5, h: 0.6,
      fontSize: 26, fontFace: 'Microsoft YaHei',
      color: theme.primary, bold: true,
      fit: 'shrink'
    });
  }
  // 标题下方装饰线
  slide.addShape(S.RECTANGLE, {
    x: 0.5, y: 1.05, w: 1.2, h: 0.04,
    fill: { color: theme.accent },
    line: { type: 'none' }
  });
  // 要点列表
  const bullets = page.bullets && page.bullets.length > 0 ? page.bullets : page.items;
  if (bullets && bullets.length > 0) {
    const useCols = bullets.length >= 4;
    const colW = useCols ? 4.5 : 9;
    const itemsPerCol = useCols ? Math.ceil(bullets.length / 2) : bullets.length;
    bullets.forEach((b, idx) => {
      const col = useCols ? Math.floor(idx / itemsPerCol) : 0;
      const row = useCols ? idx % itemsPerCol : idx;
      const x = 0.8 + col * 4.7;
      const y = 1.5 + row * 0.75;
      // 小圆点
      slide.addShape(S.OVAL, {
        x, y: y + 0.12, w: 0.12, h: 0.12,
        fill: { color: theme.accent },
        line: { type: 'none' }
      });
      slide.addText(b, {
        x: x + 0.25, y, w: colW - 0.5, h: 0.5,
        fontSize: 15, fontFace: 'Microsoft YaHei',
        color: theme.secondary, valign: 'middle'
      });
    });
  }
  addPageNum(slide, pageNum, theme, pres);
}

function renderSummary(slide, page, theme, pageNum, pres) {
  const S = pres.shapes;
  slide.background = { color: theme.primary };
  // 装饰圆圈
  slide.addShape(S.OVAL, {
    x: 7.5, y: -0.5, w: 3.0, h: 3.0,
    fill: { color: theme.accent, opacity: 12 },
    line: { type: 'none' }
  });
  slide.addShape(S.OVAL, {
    x: -1.0, y: 3.5, w: 2.5, h: 2.5,
    fill: { color: theme.light, opacity: 20 },
    line: { type: 'none' }
  });
  // 标题
  const titleText = page.title || '谢谢';
  slide.addText(titleText, {
    x: 0.5, y: 1.8, w: 9, h: 1.2,
    fontSize: 48, fontFace: 'Microsoft YaHei',
    color: 'FFFFFF', bold: true, align: 'center'
  });
  // 副标题（如果有）
  if (page.subtitle) {
    slide.addText(page.subtitle, {
      x: 0.5, y: 3.2, w: 9, h: 0.6,
      fontSize: 18, fontFace: 'Microsoft YaHei',
      color: theme.light, align: 'center'
    });
  }
  addPageNum(slide, pageNum, theme, pres);
}

function addPageNum(slide, pageNum, theme, pres) {
  const S = pres.shapes;
  const n = String(pageNum);
  slide.addShape(S.ROUNDED_RECTANGLE, {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fill: { color: theme.accent },
    line: { type: 'none' },
    rectRadius: 0.15
  });
  slide.addText(n, {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fontSize: 11, fontFace: 'Arial',
    color: 'FFFFFF', bold: true,
    align: 'center', valign: 'middle'
  });
}

function cleanContent(s) {
  s = s.replace(/<think>[\s\S]*?<\/think>/g, '');
  s = s.replace(/<think>[\s\S]*?\)/g, '');
  s = s.replace(/\*\*思考过程\*\*[\s\S]*?\*\*结束思考\*\*/g, '');
  return s.trim();
}

function cleanMarkdown(s) {
  if (!s) return '';
  // 去除 Markdown 标题标记 ###
  s = s.replace(/^#{1,6}\s+/, '');
  // 去除分隔线 ---
  s = s.replace(/^-{3,}\s*$/gm, '');
  // 去除 Markdown 粗体 **xxx** -> xxx
  s = s.replace(/\*\*(.+?)\*\*/g, '$1');
  // 去除 Markdown 斜体 *xxx* -> xxx
  s = s.replace(/\*(.+?)\*/g, '$1');
  // 去除行首的列表标记
  s = s.replace(/^[\*\-?]\s+/, '');
  // 去除行首的数字列表标记（如 1. 或 1、）
  s = s.replace(/^\d+[.、]\s+/, '');
  // 彻底清理 【】 符号（开头和末尾）
  s = s.replace(/^[\u3010\u3011]+/, '');
  s = s.replace(/[\u3010\u3011]+$/, '');
  // 合并重复的"第"字（如"第第4页" -> "第4页"）
  s = s.replace(/第+/g, '第');
  return s.trim();
}

function parseContent(content) {
  const pages = [];
  const OPEN = '\u3010';
  const CLOSE = '\u3011';

  // 先尝试用 【】 格式分割
  const parts = content.split(OPEN);

  if (parts.length > 1) {
    // 标准格式解析
    for (let i = 1; i < parts.length; i++) {
      const part = OPEN + parts[i];
      const closeIdx = part.indexOf(CLOSE);
      if (closeIdx === -1) continue;

      const header = part.slice(0, closeIdx + 1);
      const rest = part.slice(closeIdx + 1);

      // 清理 header 中的 Markdown 格式后再匹配
      const cleanHeader = cleanMarkdown(header);
      // 额外清理【】（防止 cleanMarkdown 没清理干净）
      const finalHeader = cleanHeader.replace(/^[\u3010\u3011]+/, '').replace(/[\u3010\u3011]+$/, '');
      const typeMatch = finalHeader.match(/第(\d+)页[：:]?\s*(.+)/);
      if (!typeMatch) continue;

      const pageTypeRaw = typeMatch[2].toLowerCase().trim();
      const page = { type: 'content', title: '', subtitle: '', bullets: [], items: [] };

      if (pageTypeRaw.includes('封面') || pageTypeRaw.includes('cover')) {
        page.type = 'cover';
      } else if (pageTypeRaw.includes('目录') || pageTypeRaw.includes('toc')) {
        page.type = 'toc';
        page.title = '目录';  // 默认标题
      } else if (pageTypeRaw.includes('结束') || pageTypeRaw.includes('谢谢') || pageTypeRaw.includes('summary') || pageTypeRaw.includes('end')) {
        page.type = 'summary';
      } else {
        // 内容页：标题就是章节名称
        page.title = typeMatch[2].trim();
      }

      // 解析各字段（清理 Markdown 格式）
      const cleanRest = cleanMarkdown(rest);

      const titleM = cleanRest.match(/\u6807\u9898[：:]\s*([^\n]+)/);
      if (titleM) page.title = titleM[1].trim();

      const subM = cleanRest.match(/\u526f\u6807\u9898[：:]\s*([^\n]+)/);
      if (subM) page.subtitle = subM[1].trim();

      // 要点解析：使用原始行检查列表标记（避免 cleanMarkdown 先删除标记）
      const bulletLines = rest.split('\n');
      for (const line of bulletLines) {
        const originalLine = line.trim();
        if (!originalLine) continue;

        // 跳过标题行（包含【】或标题：）
        if (originalLine.includes('\u3010') || originalLine.includes('\u3011')) continue;
        if (/^(标题|副标题)[：:]/.test(originalLine)) continue;

        // 无序列表：- xxx 或 * xxx（检查原始行）
        if (/^[\*\-]\s+.+/.test(originalLine)) {
          const pt = originalLine.replace(/^[\*\-]\s+/, '').trim();
          const cleanPt = cleanMarkdown(pt);
          if (cleanPt && cleanPt.length > 1) page.bullets.push(cleanPt);
        // 要点：xxx（检查清理后的行）
        else if (/^要点[：:]\s*.+/.test(cleanMarkdown(originalLine))) {
          const rawContent = originalLine.replace(/^要点[：:]\s*/, '').trim();
          const cleanPt = cleanMarkdown(rawContent);
          if (cleanPt && cleanPt.length > 1) page.bullets.push(cleanPt);
        // 数字列表：1. xxx 或 1、xxx（检查原始行）
        else if (/^\d+[.、]\s*.+/.test(originalLine)) {
          const rawContent = originalLine.replace(/^\d+[.、]\s*/, '').trim();
          const cleanPt = cleanMarkdown(rawContent);
          if (cleanPt && cleanPt.length > 1) {
            if (page.type === 'toc') {
              page.items.push(cleanPt);
            } else {
              page.bullets.push(cleanPt);
            }
          }
        }
      }

      pages.push(page);
    }
  }

  if (pages.length === 0) return parseFallback(content);

  // 如果最后一页不是结束页，添加结束页
  if (pages.length > 0 && pages[pages.length - 1].type !== 'summary') {
    pages.push({ type: 'summary', title: '\u8c22\u8c22', subtitle: '', bullets: [], items: [] });
  }
  return pages;
}

function parseFallback(content) {
  const pages = [];
  const lines = content.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#') && !l.startsWith('---'));
  
  // 查找第一个页面标题
  let coverTitle = '演示文稿';
  let inCover = false;
  let currentPage = null;

  for (const rawLine of content.split('\n')) {
    const line = cleanMarkdown(rawLine.trim());
    if (!line) continue;

    // 检测页面标题
    const pageMatch = line.match(/^[\u3010【]?第?\s*(\d+)\s*页[：:\s]+(.+)/);
    if (pageMatch) {
      const pageTypeRaw = pageMatch[2].toLowerCase();
      if (pageTypeRaw.includes('封面') || pageTypeRaw.includes('cover')) {
        currentPage = { type: 'cover', title: '', subtitle: '', bullets: [], items: [] };
        inCover = true;
      } else if (pageTypeRaw.includes('目录') || pageTypeRaw.includes('toc')) {
        if (currentPage) pages.push(currentPage);
        currentPage = { type: 'toc', title: '目录', subtitle: '', bullets: [], items: [] };
        inCover = false;
      } else if (pageTypeRaw.includes('结束') || pageTypeRaw.includes('谢谢') || pageTypeRaw.includes('end')) {
        if (currentPage) pages.push(currentPage);
        currentPage = { type: 'summary', title: '谢谢', subtitle: '', bullets: [], items: [] };
        inCover = false;
      } else {
        if (currentPage) pages.push(currentPage);
        currentPage = { type: 'content', title: pageMatch[2], subtitle: '', bullets: [], items: [] };
        inCover = false;
      }
      continue;
    }

    if (!currentPage) continue;

    // 解析内容行
    if (currentPage.type === 'cover') {
      if (line.includes('标题') && line.includes('：')) {
        currentPage.title = line.split(/[：:]/)[1]?.trim() || currentPage.title;
      } else if (line.includes('副标题') && line.includes('：')) {
        currentPage.subtitle = line.split(/[：:]/)[1]?.trim() || currentPage.subtitle;
      }
    } else if (currentPage.type === 'toc') {
      const itemMatch = line.match(/^\d+[.、：:]\s*(.+)/);
      if (itemMatch) currentPage.items.push(itemMatch[1].trim());
    } else {
      if (line.includes('要点') && line.includes('：')) {
        const pt = line.split(/[：:]/).slice(1).join('：').trim();
        if (pt) currentPage.bullets.push(pt);
      } else if (/^[-*]\s+/.test(line)) {
        const pt = line.replace(/^[-*]\s+/, '').trim();
        if (pt) currentPage.bullets.push(pt);
      }
    }
  }

  if (currentPage) pages.push(currentPage);

  if (pages.length === 0) {
    pages.push({ type: 'content', title: '演示文稿', subtitle: '', bullets: lines.slice(0, 5), items: [] });
  }

  // 确保有结束页
  if (pages.length > 0 && pages[pages.length - 1].type !== 'summary') {
    pages.push({ type: 'summary', title: '谢谢', subtitle: '', bullets: [], items: [] });
  }

  return pages;
}

main();
