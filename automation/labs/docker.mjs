import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { randomUUID } from 'node:crypto'
import { mkdtemp, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { setTimeout as delay } from 'node:timers/promises'
import { publication } from './repository.mjs'

const exec = promisify(execFile)
export async function runDocker(args, options = {}) {
  try {
    const { stdout } = await exec('docker', args, {
      timeout: 60000,
      maxBuffer: 4 * 1024 * 1024,
      ...options
    })
    return stdout.trim()
  } catch (error) {
    // Never dump inspect output, environment variables or application logs.
    throw new Error(`Docker ${args[0]} 失败（${error.killed ? '超时' : error.code || '中断'}）`, {
      cause: error
    })
  }
}

export async function checkLab(
  lab,
  { run = runDocker, timeoutMs = 60000, stableMs = 2000, signal } = {}
) {
  if (Object.values(lab.variables).some(value => /[\r\n\0]/.test(value))) {
    throw new Error('镜像启动测试的 env 值必须为单行文本；多行文件请放入镜像')
  }
  const imageId = await run(['image', 'inspect', '--format', '{{.Id}}', lab.image], { signal })
  if (!/^sha256:[a-f0-9]{64}$/.test(imageId)) throw new Error('无法解析已构建镜像 ID')
  const name = `attackbox-check-${randomUUID()}`
  const network = `${name}-net`
  const temp = await mkdtemp(path.join(tmpdir(), 'attackbox-check-'))
  let networkCreated = false
  let containerCreated = false
  let failure
  try {
    const envFile = path.join(temp, 'env')
    await writeFile(
      envFile,
      Object.entries(lab.variables)
        .map(([key, value]) => `${key}=${value}`)
        .join('\n'),
      { mode: 0o600 }
    )
    await run(['network', 'create', '--internal', network], { signal })
    networkCreated = true
    await run(
      [
        'container',
        'create',
        '--name',
        name,
        '--network',
        network,
        '--memory',
        `${lab.resources.memoryMB}m`,
        '--memory-swap',
        `${lab.resources.memoryMB}m`,
        '--cpus',
        String(lab.resources.cpus),
        '--pids-limit',
        String(lab.resources.pidsLimit),
        '--env-file',
        envFile,
        imageId
      ],
      { signal }
    )
    containerCreated = true
    await run(['container', 'start', name], { signal })
    const deadline = Date.now() + timeoutMs
    let readySince
    while (Date.now() < deadline) {
      signal?.throwIfAborted()
      const info = JSON.parse(
        await run(
          [
            'container',
            'inspect',
            '--format',
            '{"state":{{json .State}},"networks":{{json .NetworkSettings.Networks}}}',
            name
          ],
          { signal }
        )
      )
      if (!info.state.Running || info.state.Status === 'restarting') {
        let logs = ''
        try {
          logs = await run(['container', 'logs', '--tail', '50', name])
        } catch {}
        throw new Error(
          `容器未持续运行（${info.state.Status}，exit ${info.state.ExitCode}）${logs ? `\n--- 容器日志 ---\n${logs}` : ''}`
        )
      }
      const health = info.state.Health?.Status
      if (health === 'unhealthy') throw new Error('容器 HEALTHCHECK 失败')
      const ready = !health || health === 'healthy'
      if (ready) {
        readySince ??= Date.now()
        if (Date.now() - readySince >= stableMs) return imageId
      } else readySince = undefined
      await delay(250, undefined, { signal })
    }
    throw new Error('启动测试超时：容器或 HEALTHCHECK 未就绪')
  } catch (error) {
    failure = error
    throw error
  } finally {
    // Cleanup intentionally ignores the aborted test signal.
    const errors = []
    if (containerCreated) {
      try {
        await run(['container', 'rm', '--force', name])
      } catch (error) {
        errors.push(error)
      }
    }
    if (networkCreated) {
      try {
        await run(['network', 'rm', network])
      } catch (error) {
        errors.push(error)
      }
    }
    await rm(temp, { recursive: true, force: true })
    if (errors.length)
      throw new AggregateError([...(failure ? [failure] : []), ...errors], '启动测试资源清理失败')
  }
}

export async function publishLab(lab, { owner, revision, imageId, run = runDocker, signal }) {
  const destination = publication(lab, owner, revision)
  if (!/^sha256:[a-f0-9]{64}$/.test(imageId || ''))
    throw new Error('发布必须指定已通过启动测试的镜像 ID')
  const actual = await run(['image', 'inspect', '--format', '{{.Id}}', imageId], { signal })
  if (actual !== imageId) throw new Error('通过测试的镜像已不存在')
  for (const tag of [destination.shaImage, destination.image]) {
    await run(['image', 'tag', imageId, tag], { signal })
    await run(['image', 'push', tag], { signal, timeout: 600000 })
  }
  const digests = JSON.parse(
    await run(['image', 'inspect', '--format', '{{json .RepoDigests}}', imageId], { signal })
  )
  const repository = destination.image.slice(0, destination.image.lastIndexOf(':'))
  return {
    ...destination,
    digest: digests?.find(digest => digest.startsWith(`${repository}@`)) || null
  }
}
