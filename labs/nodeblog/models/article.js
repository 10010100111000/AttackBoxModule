const mongoose = require('mongoose');

const articleSchema = new mongoose.Schema({
  title: { type: String, required: true },
  slug: { type: String, required: true, unique: true },
  description: { type: String, default: '' },
  markdown: { type: String, default: '' },
  private: { type: Boolean, default: false },
  createdAt: { type: Date, default: Date.now }
}, { versionKey: false, collection: 'articles' });

module.exports = mongoose.model('Article', articleSchema);
