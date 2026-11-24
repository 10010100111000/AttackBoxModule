const mongoose = require('mongoose');
const User = require('./models/user');
const Article = require('./models/article');

async function seed() {
  await mongoose.connect(process.env.MONGO_URL || 'mongodb://127.0.0.1:27017/blog', {
    serverSelectionTimeoutMS: 1200
  });
  // The lab-only plaintext credential mirrors the public NodeBlog writeups.
  await User.updateOne(
    { user: 'admin' },
    { $setOnInsert: { user: 'admin', password: 'IppsecSaysPleaseSubscribe' } },
    { upsert: true }
  );
  const posts = [
    { title: 'UHC Qualifiers', slug: 'uhc-qualifiers', date: '2021-12-13',
      description: 'The UHC Qualifiers are ran the First Friday of every month!',
      markdown: 'Playing boxes like this will qualify you for the monthly finals. Join us for UHC.' },
    { title: 'My First Node App', slug: 'my-first-node-app', date: '2021-12-13',
      description: 'Believe it or not this is my first NodeJS Application!',
      markdown: 'Built with Express. There are plenty of things left to improve.' },
    { title: 'test', slug: 'test', date: '2021-12-31',
      description: 'sd', markdown: 'sd' }
  ];
  for (const post of posts) {
    await Article.updateOne(
      { slug: post.slug },
      { $setOnInsert: {
        title: post.title, slug: post.slug, description: post.description,
        markdown: post.markdown, createdAt: new Date(post.date)
      } },
      { upsert: true }
    );
  }
  await mongoose.disconnect();
}
seed().catch((err) => { console.error(err.message); process.exit(1); });
