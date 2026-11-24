const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  user: { type: String, unique: true, required: true },
  password: { type: String, required: true }
}, { versionKey: false, collection: 'users' });

module.exports = mongoose.model('User', userSchema);
