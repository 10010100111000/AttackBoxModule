const express = require('express');
const crypto = require('crypto');
const User = require('../models/user');

module.exports = (_authenticated, cookie_secret) => {
  const router = express.Router();
  router.get('/', (_req, res) => res.render('login', { error: null }));

  router.post('/', async (req, res, next) => {
    try {
      const user = req.body.user;
      const password = req.body.password;
      if (typeof user === 'undefined' || typeof password === 'undefined') {
        return res.render('login', { error: 'Invalid Username' });
      }
      // Real Mongoose/MongoDB queries. JSON nested operators are NOT sanitized.
      // URL-encoded requests use extended:false and remain scalar strings.
      const exists = await User.findOne({ user }).lean();
      if (!exists) return res.render('login', { error: 'Invalid Username' });

      const account = await User.findOne({ user, password }).lean();
      if (!account) return res.render('login', { error: 'Invalid Password' });

      const sign = crypto.createHash('md5')
        .update(cookie_secret + account.user).digest('hex');
      res.cookie('auth', JSON.stringify({ user: account.user, sign }), {
        httpOnly: true, maxAge: 900000, sameSite: 'lax'
      });
      return res.redirect('/');
    } catch (err) {
      return next(err);
    }
  });
  return router;
};
