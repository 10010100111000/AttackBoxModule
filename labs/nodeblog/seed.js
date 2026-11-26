const mongoose = require('mongoose');
const fs = require('fs');
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
        markdown: post.markdown, private: false, createdAt: new Date(post.date)
      } },
      { upsert: true }
    );
  }

  const flag01 = fs.readFileSync('/run/nodeblog/flag01.txt', 'utf8').trim();
  if (flag01.length !== 21 || !flag01.startsWith('TTP{') || !flag01.endsWith('}') || !/^[a-z2-7]{16}$/.test(flag01.slice(4, -1))) {
    throw new Error('NodeBlog Flag 01 is missing or malformed');
  }
  await Article.updateOne(
    { slug: 'staff-notes' },
    { $setOnInsert: {
      title: 'Staff Notes', slug: 'staff-notes',
      description: 'Internal notes for the editorial team.',
      markdown: flag01, private: true, createdAt: new Date('2022-01-01')
    } },
    { upsert: true }
  );
  await mongoose.disconnect();
}
seed().catch((err) => { console.error(err.message); process.exit(1); });
