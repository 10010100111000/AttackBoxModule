import Redis from 'ioredis';
import { triggerXSSQueue } from '../queue.js';
import bot from '../bot/bot.js';

const redisPublisher = new Redis();

(async () => {
  try {
    await bot.launchBrowser();
    console.log('Browser initialized in worker.');
  } catch (error) {
    console.error('Error initializing browser in worker:', error);
    process.exit(1);
  }
})();

triggerXSSQueue.process(async (job) => {
  try {
    const { xssPayload } = job.data;
    if (typeof xssPayload !== 'string' || xssPayload.length === 0) {
      throw new Error('Review job has no XSS payload');
    }

    redisPublisher.publish('job_updates', JSON.stringify({
      job_id: job.id,
      status: 'started',
    }));

    await bot.visitPage(`http://127.0.0.1:8000/xss?job_id=${encodeURIComponent(job.id)}`);

    redisPublisher.publish('job_updates', JSON.stringify({
      job_id: job.id,
      status: 'finished',
      result: { success: true },
    }));
  } catch (error) {
    redisPublisher.publish('job_updates', JSON.stringify({
      job_id: job.id,
      status: 'failed',
      error: error.message,
    }));
    throw error;
  }
});

triggerXSSQueue.on('completed', (job) => {
  console.log(`Review job ${job.id} completed.`);
});

triggerXSSQueue.on('failed', (job, error) => {
  console.error(`Review job ${job.id} failed: ${error.message}`);
});

const gracefulShutdown = async () => {
  console.log('Shutting down review worker.');
  await triggerXSSQueue.close().catch(err => console.error('Error closing Bull queue:', err));
  await redisPublisher.quit().catch(err => console.error('Error closing Redis:', err));
  await bot.closeBrowser();
  process.exit(0);
};

process.on('SIGINT', gracefulShutdown);
process.on('SIGTERM', gracefulShutdown);
