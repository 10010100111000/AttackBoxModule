import { getXSSPayload } from '../utils/redis.js';

export default async function setupXSSRoutes(fastify) {
  fastify.get('/xss', async (req, reply) => {
    try {
      const payload = await getXSSPayload(req.query.job_id);
      return reply.view('xss.ejs', {
        payload,
        vite: req.viteAssets
      });
    } catch (error) {
      fastify.log.error(error);
      return reply.code(500).send({ success: false, message: 'Error fetching payload.' });
    }
  });
}
