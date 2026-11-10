const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { test } = require('node:test');
const { getProcessor } = require('bytemd');

const skill = resolve(__dirname, '../../skills/personal/skill-blog-writer');

function examples(file) {
  return [...readFileSync(resolve(skill, file), 'utf8').matchAll(/```html\n([\s\S]*?)\n```/g)]
    .map(match => match[1]);
}

function elements(node, tag) {
  return [
    ...(node.type === 'element' && node.tagName === tag ? [node] : []),
    ...(node.children || []).flatMap(child => elements(child, tag)),
  ];
}

function text(node) {
  return node.type === 'text' ? node.value : (node.children || []).map(text).join('');
}

function render(source, removePresentation = false) {
  const processor = getProcessor(removePresentation ? {
    sanitize(schema) {
      // Exercise the strict target without allowing style or other new attributes.
      for (const key of Object.keys(schema.attributes)) {
        schema.attributes[key] = schema.attributes[key].filter(attribute =>
          !['style', 'className', 'id'].includes(Array.isArray(attribute) ? attribute[0] : attribute));
      }
      return schema;
    },
  } : {});
  return processor.runSync(processor.parse(source));
}

function rows(tree) {
  return elements(tree, 'tr').map(row => row.children
    .filter(child => child.type === 'element' && ['th', 'td'].includes(child.tagName))
    .map(cell => text(cell).trim()));
}

function checkFigure(source) {
  const tree = render(`${source}\n\n图后的正文。`);
  assert.equal(elements(tree, 'table').length, 1, 'the diagram must retain rows and columns after ByteMD sanitization');
  assert.equal(elements(tree, 'pre').length, 0, 'the final HTML must render rather than appear as a code block');
  assert.ok(tree.children.some(node => node.tagName === 'p' && text(node) === '图后的正文。'));
  assert.deepEqual(rows(render(source, true)), rows(tree), 'relationships must survive removal of presentation attributes');
  return rows(tree);
}

test('main example preserves the equal-key record order as a table', () => {
  const figures = examples('SKILL.md');
  assert.equal(figures.length, 1);
  assert.deepEqual(checkFigure(figures[0]), [
    ['阶段', '键相同的两条记录'],
    ['输入', 'A → B'],
    ['稳定排序后', 'A → B'],
    ['不稳定的一种输出', 'B → A'],
  ]);
});

test('GQA example retains each Q group and its shared K/V pair', () => {
  const figures = examples('references/html-figures.md');
  assert.deepEqual(checkFigure(figures[0]), [
    ['Q 头', '共享的 K、V', '每个向量'],
    ['Q 0–3', 'K₀、V₀', '128 个元素'],
    ['Q 4–7', 'K₁、V₁', '128 个元素'],
    ['Q 8–27', 'K₂–K₆、V₂–V₆（5 组）', '128 个元素'],
    ['Q 28–31', 'K₇、V₇', '128 个元素'],
  ]);
});

test('serial compression example retains stages, units and totals', () => {
  const figures = examples('references/html-figures.md');
  assert.equal(figures.length, 2);
  const actual = checkFigure(figures[1]);
  assert.deepEqual(actual, [
    ['依次执行的阶段', '直接传输', '压缩后传输'],
    ['① 压缩', '0 s', '7 s'],
    ['② 传输', '10 s', '4 s'],
    ['③ 解压', '0 s', '1 s'],
    ['总耗时', '10 s', '12 s'],
  ]);
  for (const column of [1, 2]) {
    assert.equal(actual.slice(1, 4).reduce((sum, row) => sum + parseInt(row[column], 10), 0), parseInt(actual[4][column], 10));
  }
});

test('default ByteMD still strips inline layout and active content', () => {
  const tree = render('<div style="display:flex" onclick="alert(1)"><span>7 s</span><span>4 s</span></div><script>alert(1)</script>');
  assert.equal(elements(tree, 'div')[0].properties.style, undefined);
  assert.equal(elements(tree, 'div')[0].properties.onClick, undefined);
  assert.equal(elements(tree, 'script').length, 0);
  assert.equal(text(tree), '7 s4 s');
});
