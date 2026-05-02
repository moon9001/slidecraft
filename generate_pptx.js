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
    '默认':   { primary:'1A3A6F',secondary:'2D5A2D',accent:'4A7C4A',light:'8FBC8F',bg:'FFFFFF' },
    '森林墨': { primary:'1A3A6F',secondary:'2D5A2D',accent:'4A7C4A',light:'8FBC8F',bg:'F0F8F0' },
    '科技蓝': { primary:'1E3A5F',secondary:'2E5A8F',accent:'4A90D9',light:'A8D4FF',bg:'F0F5FF' },
    '樱粉':   { primary:'8B3A62',secondary:'D4708A',accent:'E8A0B0',light:'F5D0D8',bg:'FFF5F7' },
    '星空蓝': { primary:'1A1A2E',secondary:'16213E',accent:'0F3460',light:'4A90D9',bg:'F0F4FF' },
  };
  const theme = themes[themeName] || themes['默认'];

  pages.forEach((page, i) => {
    const slide = pres.addSlide();
    switch (page.type) {
      case 'cover':  renderCover(slide, page, theme); break;
      case 'toc':    renderToc(slide, page, theme, i + 1); break;
      case 'content': renderContent(slide, page, theme, i + 1); break;
      case 'summary': renderSummary(slide, page, theme, i + 1); break;
      default: renderContent(slide, page, theme, i + 1);
    }
  });

  const tmpFile = path.join(__dirname, `tmp_${Date.now()}.pptx`);
  await pres.writeFile({ fileName: tmpFile });
  const buffer = fs.readFileSync(tmpFile);
  fs.unlinkSync(tmpFile);
  return buffer;
}

function cleanContent(s) {
  s = s.replace(/<think>[\s\S]*?<\/think>/g, '');
  s = s.replace(/<think>[\s\S]*?\)/g, '');
  s = s.replace(/\*\*思考过程\*\*[\s\S]*?\*\*结束思考\*\*/g, '');
  return s.trim();
}

function parseContent(content) {
  const pages = [];

  // 用 【 分割成块，每个块格式：第N页：类型】内容
  // 第1个块没有 【 ，所以要跳过或当作无效
  const OPEN = '\u3010';  // 【
  const CLOSE = '\u3011';  // 】

  const parts = content.split(OPEN);

  for (let i = 1; i < parts.length; i++) {
    const part = OPEN + parts[i];  // 重新加上 【
    // part 格式：【第N页：类型】内容【第N+1页：类型】...

    // 找第一个 】 的位置
    const closeIdx = part.indexOf(CLOSE);
    if (closeIdx === -1) continue;

    const header = part.slice(0, closeIdx + 1);  // 【第N页：类型】
    const rest = part.slice(closeIdx + 1);  // 内容...

    // 提取类型 (冒号可选，类型内容可以是空的)
    const typeMatch = header.match(/\u7b2c(\d+)\u9875[：:]?([^\u3011]*)/);  // 第N页：类型（或第N页类型）
    if (!typeMatch) continue;

    const pageType = typeMatch[2].trim().toLowerCase();
    const page = { type: 'content', title: '', subtitle: '', bullets: [], items: [] };

    // 判断页面类型
    if (pageType.includes('\u5c01\u9762') || pageType.includes('cover')) {  // 封面
      page.type = 'cover';
    } else if (pageType.includes('\u76ee\u5f55') || pageType.includes('toc')) {  // 目录
      page.type = 'toc';
    } else if (pageType.includes('\u7ed3\u675f') || pageType.includes('\u8c22\u8c22') || pageType.includes('summary')) {  // 结束, 谢谢
      page.type = 'summary';
    }

    // 提取标题
    const titleM = rest.match(/\u6807\u9898[：:]\s*([^\u3010\u3011\n]+)/);  // 标题：
    if (titleM) page.title = titleM[1].trim();

    // 提取副标题
    const subM = rest.match(/\u526f\u6807\u9898[：:]\s*([^\u3010\u3011\n]+)/);  // 副标题：
    if (subM) page.subtitle = subM[1].trim();

    // 提取要点
    const bulletMs = rest.match(/\u8981\u70b9[：:]\s*([^\u3010\u3011\n]+)/g);  // 要点：
    if (bulletMs) page.bullets = bulletMs.map(b => b.replace(/\u8981\u70b9[：:]\s*/, '').trim());

    // 提取编号列表
    const itemMs = rest.match(/(\d+)[\.、：:]\s*([^\u3010\u3011\n]+)/g);
    if (itemMs) page.items = itemMs.map(x => {
      const m = x.match(/(\d+)[\.、：:]\s*([^\u3010\u3011\n]+)/);
      return m ? m[2].trim() : x.trim();
    });

    pages.push(page);
  }

  if (pages.length === 0) return parseFallback(content);

  // 确保最后一个页面是 summary
  if (pages.length > 0 && pages[pages.length - 1].type !== 'summary') {
    pages.push({ type: 'summary', title: '\u8c22\u8c22', subtitle: '', bullets: [], items: [] });  // 谢谢
  }
  return pages;
}

function parseFallback(content) {
  const pages = [];
  const lines = content.split('\n').map(l => l.trim()).filter(Boolean);
  let title = '演示文稿';
  for (const l of lines) { const m = l.match(/^\*([^*]+)\*$/); if (m) { title = m[1].trim(); break; } }
  const bullets = lines.filter(l => /^[-?\*]\s/.test(l)).map(l => l.replace(/^[-?\*]\s*/, '').trim());
  if (bullets.length > 0) {
    pages.push({ type: 'content', title, subtitle: '', bullets, items: [] });
  } else if (lines.length > 0) {
    pages.push({ type: 'content', title: lines[0], subtitle: '', bullets: lines.slice(1), items: [] });
  }
  pages.push({ type: 'summary', title: '谢谢', subtitle: '', bullets: [], items: [] });
  return pages;
}

function renderCover(slide, page, theme) {
  slide.background = { color: theme.primary };
  if (page.title) slide.addText(page.title, { x:0.5, y:2.0, w:9, h:1.5, fontSize:44, fontFace:'Microsoft YaHei', color:'FFFFFF', bold:true, align:'center' });
  if (page.subtitle) slide.addText(page.subtitle, { x:0.5, y:3.8, w:9, h:0.6, fontSize:20, fontFace:'Microsoft YaHei', color:theme.light, align:'center' });
}
function renderToc(slide, page, theme, pageNum) {
  slide.background = { color: theme.bg };
  slide.addText('目录', { x:0.5, y:0.5, w:9, h:0.8, fontSize:32, fontFace:'Microsoft YaHei', color:theme.primary, bold:true });
  const items = page.items.length > 0 ? page.items : page.bullets;
  if (items.length > 0) items.forEach((item, idx) => {
    const y = 1.5 + idx * 0.7;
    slide.addText(`${idx + 1}. ${item}`, { x:1.0, y, w:8, h:0.5, fontSize:18, fontFace:'Microsoft YaHei', color:theme.secondary });
  });
  addPageNum(slide, pageNum, theme);
}
function renderContent(slide, page, theme, pageNum) {
  slide.background = { color: theme.bg };
  if (page.title) slide.addText(page.title, { x:0.5, y:0.5, w:9, h:0.7, fontSize:26, fontFace:'Microsoft YaHei', color:theme.primary, bold:true });
  if (page.bullets && page.bullets.length > 0) {
    const textArray = page.bullets.map((b, idx) => ({
      text: b, options: { bullet:true, breakLine: idx < page.bullets.length - 1, fontSize:15, fontFace:'Microsoft YaHei', color:theme.secondary }
    }));
    slide.addText(textArray, { x:0.8, y:1.5, w:8.5, h:3.5 });
  }
  addPageNum(slide, pageNum, theme);
}
function renderSummary(slide, page, theme, pageNum) {
  slide.background = { color: theme.primary };
  slide.addText(page.title || '谢谢', { x:0.5, y:2.0, w:9, h:1.2, fontSize:48, fontFace:'Microsoft YaHei', color:'FFFFFF', bold:true, align:'center' });
  addPageNum(slide, pageNum, theme);
}
function addPageNum(slide, pageNum, theme) {
  slide.addShape('oval', { x:9.3, y:5.1, w:0.4, h:0.4, fill:{ color:theme.accent }, line:{ type:'none' } });
  slide.addText(String(pageNum), { x:9.3, y:5.1, w:0.4, h:0.4, fontSize:12, fontFace:'Arial', color:'FFFFFF', bold:true, align:'center', valign:'middle' });
}
main();
