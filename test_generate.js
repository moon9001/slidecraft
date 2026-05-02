#!/usr/bin/env node
/**
 * generate_pptx.js 自动化测试脚本 (异步版)
 * 测试多种输入，验证输出的 PPTX 文件 slide 数量是否正确
 */

const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const JSZip = require('jszip');

const TEST_CASES = [
  {
    name: '标准四页',
    content: '【第1页：封面】标题：测试PPT 副标题：这是一个测试 【第2页：目录】1. 第一点 2. 第二点 【第3页：内容】标题：主要内容 要点：第一点内容 要点：第二点内容 【第4页：结束】',
    expectSlides: 4,
  },
  {
    name: '含AI思考过程',
    content: '<think>这是思考过程，要被清理掉）【第1页：封面】标题：清理测试 副标题：思考过程应消失 【第2页：内容】标题：内容页 要点：要点1 要点：要点2 【第3页：结束】',
    expectSlides: 3,
  },
  {
    name: '只有封面和结束',
    content: '【第1页：封面】标题：简单PPT 【第2页：结束】',
    expectSlides: 2,
  },
  {
    name: '多个内容页',
    content: '【第1页：封面】标题：多页测试 【第2页：内容】标题：第一章 要点：要点一 要点：要点二 【第3页：内容】标题：第二章 要点：要点A 要点：要点B 【第4页：结束】',
    expectSlides: 4,
  },
  {
    name: '含 think 闭合标签',
    content: '<think>思考中...</think>【第1页：封面】标题：Think测试 【第2页：内容】标题：内容 要点：要点1 【第3页：结束】',
    expectSlides: 3,
  },
];

const scriptPath = path.join(__dirname, 'generate_pptx.js');

function execFileAsync(cmd, args, opts) {
  return new Promise((resolve, reject) => {
    const proc = execFile(cmd, args, opts, (err, stdout, stderr) => {
      if (err) { err.stdout = stdout; err.stderr = stderr; reject(err); return; }
      resolve({ stdout, stderr });
    });
  });
}

async function runTest(tc) {
  console.log(`📝 测试：${tc.name}`);
  console.log(`   期望 slide 数：${tc.expectSlides}`);

  const input = JSON.stringify({
    title: tc.name,
    content: tc.content,
    themeName: '默认',
  });

  let stdout, stderr, exitCode;
  try {
    const result = await execFileAsync('node', [scriptPath, input], {
      timeout: 30000,
      encoding: 'utf8',
    });
    stdout = result.stdout;
    stderr = result.stderr;
    exitCode = 0;
  } catch (e) {
    stdout = e.stdout || '';
    stderr = e.stderr || '';
    exitCode = e.code || 1;
  }

  if (exitCode !== 0) {
    console.log(`   ❌ 进程退出码：${exitCode}`);
    if (stderr) console.log(`   错误：${stderr.slice(0, 300)}`);
    console.log('');
    return false;
  }

  // stdout 应该是 base64 编码的 PPTX
  const b64 = (stdout || '').trim();
  if (!b64) {
    console.log('   ❌ 输出为空');
    console.log('');
    return false;
  }

  // 用 JSZip 验证 slide 数量
  let slideCount = 0;
  try {
    const buf = Buffer.from(b64, 'base64');
    const zip = await JSZip.loadAsync(buf);
    const slideFiles = Object.keys(zip.files).filter(name => /^ppt\/slides\/slide\d+\.xml$/.test(name));
    slideCount = slideFiles.length;
  } catch (e) {
    console.log(`   ❌ ZIP 验证失败：${e.message.slice(0, 100)}`);
    console.log('');
    return false;
  }

  console.log(`   实际 slide 数：${slideCount}`);
  if (slideCount === tc.expectSlides) {
    console.log(`   ✅ 通过`);
    console.log('');
    return true;
  } else {
    console.log(`   ❌ 失败：期望 ${tc.expectSlides}，实际 ${slideCount}`);
    if (stderr) console.log(`   DEBUG: ${stderr.slice(0, 200)}`);
    console.log('');
    return false;
  }
}

async function main() {
  console.log('=== generate_pptx.js 自动化测试开始 ===\n');
  let passed = 0;
  let failed = 0;

  for (const tc of TEST_CASES) {
    const ok = await runTest(tc);
    if (ok) passed++; else failed++;
  }

  console.log('=== 测试结束 ===');
  console.log(`✅ 通过：${passed}   ❌ 失败：${failed}`);
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => {
  console.error('测试脚本异常:', err);
  process.exit(2);
});
