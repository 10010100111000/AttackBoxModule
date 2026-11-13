#!/usr/bin/env node
import { parseArgs } from 'node:util'
import { appendFile } from 'node:fs/promises'
import { planLabs, loadLab } from './repository.mjs'
import { checkLab, publishLab } from './docker.mjs'

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    root: { type: 'string', default: '.' },
    directory: { type: 'string' },
    owner: { type: 'string' },
    revision: { type: 'string' },
    base: { type: 'string' },
    'image-id': { type: 'string' },
    timeout: { type: 'string', default: '60' }
  }
})
const abort = new AbortController()
for (const event of ['SIGINT', 'SIGTERM']) process.once(event, () => abort.abort(new Error(event)))

try {
  switch (positionals[0]) {
    case 'plan': {
      if (!values.owner || !values.revision) throw new Error('plan 需要 --owner 和 --revision')
      const matrix = await planLabs(values)
      console.log(JSON.stringify(matrix, null, 2))
      if (process.env.GITHUB_OUTPUT)
        await appendFile(
          process.env.GITHUB_OUTPUT,
          `matrix=${JSON.stringify(matrix)}\ncount=${matrix.include.length}\n`
        )
      break
    }
    case 'check': {
      if (!values.directory) throw new Error('check 需要 --directory')
      const timeout = Number(values.timeout)
      if (!Number.isInteger(timeout) || timeout < 1 || timeout > 600)
        throw new Error('timeout 必须为 1–600 秒')
      const lab = await loadLab(values.root, values.directory)
      const imageId = await checkLab(lab, {
        timeoutMs: timeout * 1000,
        signal: abort.signal
      })
      console.log(`启动测试通过: ${lab.image} (${imageId})`)
      if (process.env.GITHUB_OUTPUT)
        await appendFile(process.env.GITHUB_OUTPUT, `image-id=${imageId}\n`)
      break
    }
    case 'publish': {
      if (!values.directory || !values.owner || !values.revision)
        throw new Error('publish 需要 --directory、--owner、--revision 和 --image-id')
      const lab = await loadLab(values.root, values.directory)
      const result = await publishLab(lab, {
        owner: values.owner,
        revision: values.revision,
        imageId: values['image-id'],
        signal: abort.signal
      })
      console.log(JSON.stringify(result, null, 2))
      if (process.env.GITHUB_STEP_SUMMARY)
        await appendFile(
          process.env.GITHUB_STEP_SUMMARY,
          `\n发布成功：\`${result.image}\`\n\n提交标签：\`${result.shaImage}\`\n\nDigest：\`${result.digest || '见 GHCR'}\`\n`
        )
      break
    }
    default:
      throw new Error(
        '用法: node automation/labs/cli.mjs plan|check|publish [--directory ...] [--owner ...] [--revision ...]'
      )
  }
} catch (error) {
  console.error(error.message)
  process.exitCode = 1
}
