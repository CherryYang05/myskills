const fs = require('node:fs');
const path = require('node:path');
const { getProcessor } = require('bytemd');

const plugins = ['gfm', 'math', 'breaks'].map((name) => {
  const plugin = require('@bytemd/plugin-' + name);
  return (plugin.default ?? plugin)();
});

function requiredText(meta, key) {
  const value = meta[key];
  if (typeof value !== 'string' || !value.trim() || /[\r\n]/.test(value)) {
    throw new Error(key + ' must be a nonempty line');
  }
  return value.trim();
}

function taxonomy(meta, key, min, max) {
  const values = meta[key];
  if (!Array.isArray(values) || values.length < min || values.length > max ||
      values.some((value) => typeof value !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(value)) ||
      new Set(values).size !== values.length) {
    throw new Error(key + ' must contain ' + min + '–' + max + ' distinct Halo metadata.name values');
  }
  return values;
}

function checkFigureMarkup(node) {
  if (node.type === 'html' && /<\/?(?:svg|iframe|script|style|object|embed)\b/i.test(node.value)) {
    throw new Error('Unsupported HTML in article. Put interactive markup in a separate HTML file.');
  }
  for (const child of node.children ?? []) checkFigureMarkup(child);
}

function buildDraft(markdown, meta) {
  const title = requiredText(meta, 'title');
  const slug = requiredText(meta, 'slug');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || slug.length > 50) {
    throw new Error('slug must contain lowercase ASCII words separated by hyphens, up to 50 characters');
  }
  const categories = taxonomy(meta, 'categories', 1, 1);
  const tags = taxonomy(meta, 'tags', 1, 5);
  const raw = markdown.trim().replace(/^\uFEFF/, '');
  const firstLine = raw.split(/\r?\n/, 1)[0];
  if (firstLine !== '# ' + title) throw new Error('The first Markdown line must match the title');
  const body = raw.slice(firstLine.length).trim();
  if (!body) throw new Error('Markdown body is empty');

  const processor = getProcessor({
    plugins,
    sanitize: (schema) => ({
      ...schema,
      attributes: {
        ...schema.attributes,
        '*': [...(schema.attributes?.['*'] ?? []), 'style'],
      },
    }),
  });
  checkFigureMarkup(processor.parse(body));
  const rendered = String(processor.processSync(body));
  if (/<code class="language-mermaid(?: |")/i.test(rendered)) {
    throw new Error('Mermaid requires the Halo editor renderer. Use a static HTML figure or save in ByteMD.');
  }

  return {
    post: {
      apiVersion: 'content.halo.run/v1alpha1',
      kind: 'Post',
      metadata: { name: 'blog-' + slug },
      spec: {
        title,
        slug,
        deleted: false,
        publish: false,
        pinned: false,
        allowComment: true,
        visible: 'PUBLIC',
        priority: 0,
        excerpt: { autoGenerate: true },
        categories,
        tags,
      },
    },
    content: { raw: body + '\n', content: rendered, rawType: 'markdown' },
  };
}

try {
  const [article, metadata, output, ...extra] = process.argv.slice(2);
  if (!article || !metadata || !output || extra.length || path.extname(output) !== '.json') {
    throw new Error('Usage: node prepare-halo.cjs <article.md> <halo-meta.json> <halo-draft.json>');
  }
  const preview = output.replace(/\.json$/, '.preview.html');
  if ([article, metadata].some((source) => [output, preview].some(
    (destination) => path.resolve(source) === path.resolve(destination),
  ))) throw new Error('Output paths must differ from input paths');

  const draft = buildDraft(
    fs.readFileSync(article, 'utf8'),
    JSON.parse(fs.readFileSync(metadata, 'utf8')),
  );
  const previewHtml = '<!doctype html><html lang="zh-CN"><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>ByteMD 正文预览</title>' +
    '<main style="max-width:48rem;margin:2rem auto;padding:0 1rem;line-height:1.65">' +
    draft.content.content + '</main></html>\n';
  fs.writeFileSync(preview, previewHtml);
  fs.writeFileSync(output, JSON.stringify(draft, null, 2) + '\n');
  console.log(preview + '\n' + output);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
