const express = require('express');
const mongoose = require('mongoose');
const Article = require('./models/article');
const serialize = require('node-serialize');
const fileUpload = require('express-fileupload');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');

const cookie_secret = 'UHC-SecretCookie';
const app = express();

app.set('view engine', 'ejs');
app.set('views', '/opt/blog/views');
app.use(express.urlencoded({ extended: false }));
app.use(fileUpload({ limits: { fileSize: 1024 * 1024 }, abortOnLimit: true }));
app.use(express.json());
app.use(cookieParser());
app.use(express.static('/opt/blog/public', { index: false }));

// Actual vulnerable node-serialize <=0.0.4: functions evaluate during
// unserialize(), before the application performs its subsequent signature check.
function authenticated(c) {
  if (typeof c === 'undefined') return false;
  try {
    c = serialize.unserialize(c);
    return Boolean(c && c.sign === crypto.createHash('md5')
      .update(cookie_secret + c.user).digest('hex'));
  } catch (_err) {
    return false;
  }
}
const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

app.get('/healthz', wrap(async (_req, res) => {
  await mongoose.connection.db.admin().ping();
  res.json({ web: 'ok', mongodb: 'ok' });
}));

app.get('/', wrap(async (req, res) => {
  const articles = await Article.find().sort({ createdAt: -1 }).lean();
  res.render('articles/index', { articles, authenticated: authenticated(req.cookies.auth) });
}));

app.use('/login', require('./routes/login')(authenticated, cookie_secret));
app.use('/articles', require('./routes/articles')(authenticated));

app.use((err, _req, res, _next) => {
  // The upstream lab's development stack also disclosed parser stack traces.
  res.status(500).type('text/plain').send(err.stack || String(err));
});

mongoose.connect(process.env.MONGO_URL || 'mongodb://127.0.0.1:27017/blog')
  .then(() => app.listen(Number(process.env.PORT || 5000), '0.0.0.0',
    () => console.log('Blog listening on port 5000')))
  .catch((err) => { console.error('Mongo connection failed', err); process.exit(1); });
