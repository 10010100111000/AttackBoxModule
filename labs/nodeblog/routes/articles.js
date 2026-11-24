const express = require('express');
const libxmljs = require('libxmljs2');
const Article = require('../models/article');

module.exports = (authenticated) => {
  const router = express.Router();
  const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
  function requireAuth(req, res, next) {
    if (!authenticated(req.cookies.auth)) return res.redirect('/login');
    return next();
  }

  router.get('/new', requireAuth, (_req, res) => {
    res.render('articles/new', { prefill: { title: '', description: '', markdown: '' } });
  });

  // Native libxml2 entity resolution, not a hand-written XML or file-read shim.
  router.post('/xml', requireAuth, (req, res) => {
    const file = req.files && req.files.file;
    const invalid = 'Invalid XML Example: <post><title>Example Post</title><description>Example Description</description><markdown>Example Markdown</markdown></post>';
    if (!file || Array.isArray(file)) return res.type('text/plain').send(invalid);
    try {
      const doc = libxmljs.parseXmlString(file.data.toString('utf8'), {
        noent: true, noblanks: true
      });
      const root = doc.root();
      if (!root || root.name() !== 'post') throw new Error('Not a post');
      const field = (name) => {
        const element = root.get('./' + name);
        if (!element) throw new Error('Missing field ' + name);
        return element.text();
      };
      return res.render('articles/new', { prefill: {
        title: field('title'), description: field('description'),
        markdown: field('markdown')
      } });
    } catch (_err) {
      return res.type('text/plain').send(invalid);
    }
  });

  router.post('/', requireAuth, wrap(async (req, res) => {
    const title = String(req.body.title || '').slice(0, 200);
    const description = String(req.body.description || '').slice(0, 4000);
    const markdown = String(req.body.markdown || '').slice(0, 20000);
    if (!title) return res.redirect('/articles/new');
    const slugBase = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'article';
    const slug = slugBase + '-' + Date.now().toString(36);
    await Article.create({ title, slug, description, markdown });
    res.redirect('/articles/' + slug);
  }));

  router.get('/:slug', wrap(async (req, res) => {
    const article = await Article.findOne({ slug: req.params.slug }).lean();
    if (!article) return res.status(404).send('Not Found');
    res.render('articles/show', { article, authenticated: authenticated(req.cookies.auth) });
  }));

  router.get('/:slug/edit', requireAuth, wrap(async (req, res) => {
    const article = await Article.findOne({ slug: req.params.slug }).lean();
    if (!article) return res.status(404).send('Not Found');
    res.render('articles/new', { prefill: article });
  }));
  return router;
};
