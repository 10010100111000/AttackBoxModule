import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { parse } from 'yaml'
import { validateLabConfig } from './lab-spec.mjs'
import { loadLab, planLabs, publication } from './repository.mjs'
import { checkLab, publishLab, runDocker } from './docker.mjs'

const exec = promisify(execFile)
const revision = 'a'.repeat(40)
const id = `sha256:${'b'.repeat(64)}`
const config = () =>
  validateLabConfig({
    image: 'ghcr.io/example/demo:latest',
    env: { SECRET: 'not-for-output' }
  })

async function fixture(t) {
  const root = await mkdtemp(path.join(tmpdir(), 'lab-publisher-test-'))
  t.after(() => rm(root, { recursive: true, force: true }))
  const git = async (...args) => (await exec('git', args, { cwd: root })).stdout.trim()
  await git('init', '-q')
  await git('config', 'user.email', 'test@example.invalid')
  await git('config', 'user.name', 'publisher-test')
  const add = async (directory, image = 'ghcr.io/example/demo:latest') => {
    await mkdir(path.join(root, directory, 'files'), { recursive: true })
    await writeFile(path.join(root, directory, 'lab.yml'), `image: ${image}\n`)
    await writeFile(path.join(root, directory, 'Dockerfile'), 'FROM nginx:1.27-alpine\n')
    await writeFile(path.join(root, directory, 'Tutorial.md'), '# Lesson\n')
    await writeFile(path.join(root, directory, 'files', 'exercise.md'), 'fixture\n')
  }
  const commit = async () => {
    await git('add', '.')
    await git('commit', '-qm', 'fixture')
    return git('rev-parse', 'HEAD')
  }
  return { root, git, add, commit }
}

test('shared author contract: defaults, limits and unsupported fields', () => {
  assert.deepEqual(config().resources, {
    memoryMB: 512,
    cpus: 1,
    pidsLimit: 256
  })
  for (const input of [
    null,
    [],
    { image: 'nginx', compose: {} },
    { image: 'nginx', limits: { memory: 1 } },
    { image: 'nginx', env: { BAD: null } },
    { image: 'nginx', port: 65536 }
  ]) {
    assert.throws(() => validateLabConfig(input))
  }
  assert.equal(
    validateLabConfig({ image: 'nginx:alpine', env: { N: 2, B: false } }).variables.B,
    'false'
  )
})

test('publish destinations belong to owner, use explicit tags and reserve sha tags', () => {
  assert.equal(
    publication(config(), 'Example', revision).shaImage,
    `ghcr.io/example/demo:latest-sha-${revision}`
  )
  for (const image of [
    'nginx:latest',
    'ghcr.io/other/demo:latest',
    'ghcr.io/example/demo',
    `ghcr.io/example/demo@sha256:${'a'.repeat(64)}`,
    'ghcr.io/example/demo:sha-manual',
    `ghcr.io/example/demo:files-sha-${revision}`,
    'ghcr.io/example/demo:' + 'a'.repeat(84)
  ]) {
    assert.throws(() => publication({ ...config(), image }, 'example', revision))
  }
  assert.throws(() => publication(config(), 'example', 'main'))
})

test('planning discovers new labs and avoids rebuilding tutorial-only edits', async t => {
  const { root, add, commit } = await fixture(t)
  await add('challenges/demo')
  const first = await commit()
  const plan = options => planLabs({ root, owner: 'example', revision: first, ...options })
  assert.equal((await plan({ base: '0'.repeat(40) })).include.length, 1)
  const serialized = JSON.stringify(await plan({}))
  assert.ok(!serialized.includes('SECRET'))
  await writeFile(path.join(root, 'challenges/demo/Tutorial.md'), '# Updated\n')
  const second = await commit()
  assert.deepEqual((await plan({ base: first, revision: second })).include, [])
  await writeFile(path.join(root, 'challenges/demo/files/exercise.md'), 'updated\n')
  const third = await commit()
  assert.equal((await plan({ base: second, revision: third })).include.length, 1)
  await add('modules/new', 'ghcr.io/example/new:latest')
  const fourth = await commit()
  assert.deepEqual(
    (await plan({ base: third, revision: fourth })).include.map(lab => lab.directory),
    ['modules/new']
  )
  assert.equal((await plan({ base: 'f'.repeat(40), revision: fourth })).include.length, 2)
  assert.equal((await plan({ directory: 'modules/new', revision: fourth })).include.length, 1)
  await assert.rejects(plan({ directory: 'does-not-exist', revision: fourth }))
})

test('planning includes deletions, renames and publisher changes; skips external images without Dockerfile', async t => {
  const { root, git, add, commit } = await fixture(t)
  await add('labs/demo')
  await mkdir(path.join(root, 'external'))
  await writeFile(path.join(root, 'external/lab.yml'), 'image: nginx:alpine')
  const first = await commit()
  await git('mv', 'labs/demo/files/exercise.md', 'labs/demo/files/renamed.md')
  const second = await commit()
  const plan = (base, revision) => planLabs({ root, owner: 'example', base, revision })
  assert.equal((await plan(first, second)).include.length, 1)
  await rm(path.join(root, 'labs/demo/files/renamed.md'))
  const third = await commit()
  assert.equal((await plan(second, third)).include.length, 1)
  await mkdir(path.join(root, 'automation/labs'), { recursive: true })
  await writeFile(path.join(root, 'automation/labs/cli.mjs'), '// updated')
  const fourth = await commit()
  assert.equal((await plan(third, fourth)).include.length, 1)
  await add('labs/duplicate')
  await assert.rejects(planLabs({ root, owner: 'example', revision: fourth }), /不同靶机/)
})

test('different labs share one GHCR package with distinct stable and immutable tags', async t => {
  const { root, add, commit } = await fixture(t)
  await add('modules/files', 'ghcr.io/example/attackbox-labs:files')
  await add('challenges/web', 'ghcr.io/example/attackbox-labs:web')
  const revision = await commit()
  const plan = await planLabs({ root, owner: 'example', revision })
  assert.equal(plan.include.length, 2)
  const destinations = plan.include.map(lab => publication(lab, 'example', revision))
  assert.equal(new Set(destinations.map(lab => lab.shaImage)).size, 2)
})

test('declarations reject duplicates, aliases, both filenames and symbolic files', async t => {
  const { root, add } = await fixture(t)
  await add('lab')
  for (const yaml of [
    'image: nginx\nimage: redis\n',
    'image: nginx\nenv: &env { A: 1 }\nlimits: *env\n'
  ]) {
    await writeFile(path.join(root, 'lab/lab.yml'), yaml)
    await assert.rejects(loadLab(root, 'lab'))
  }
  await writeFile(path.join(root, 'lab/lab.yaml'), 'image: nginx\n')
  await assert.rejects(loadLab(root, 'lab'), /只保留一个/)
  await rm(path.join(root, 'lab/lab.yaml'))
  await rm(path.join(root, 'lab/lab.yml'))
  await writeFile(path.join(root, 'outside.yml'), 'image: nginx')
  await symlink('../outside.yml', path.join(root, 'lab/lab.yml'))
  await assert.rejects(loadLab(root, 'lab'), /普通文件/)
  await assert.rejects(planLabs({ root, owner: 'example', revision }), /普通文件/)
  await assert.rejects(loadLab(root, '..'), /仓库内/)
})

function fakeDocker({ health, running = true, failCreate = false } = {}) {
  const calls = []
  let network
  const run = async args => {
    calls.push(args)
    if (args[0] === 'image' && args[1] === 'inspect') {
      return args.includes('{{json .RepoDigests}}')
        ? JSON.stringify([`ghcr.io/example/demo@sha256:${'c'.repeat(64)}`])
        : id
    }
    if (args[0] === 'network' && args[1] === 'create') network = args.at(-1)
    if (args[0] === 'container' && args[1] === 'create') {
      const envFile = args[args.indexOf('--env-file') + 1]
      assert.match(await readFile(envFile, 'utf8'), /SECRET=not-for-output/)
      if (failCreate) throw new Error('create failed')
    }
    if (args[0] === 'container' && args[1] === 'inspect')
      return JSON.stringify({
        state: {
          Running: running,
          Status: running ? 'running' : 'exited',
          ExitCode: running ? 0 : 1,
          ...(health ? { Health: { Status: health } } : {})
        },
        networks: { [network]: { IPAddress: '10.1.0.2' } }
      })
    return ''
  }
  return { calls, run }
}

test('smoke test uses tested ID, resource limits and isolated network, cleans up before publishing', async () => {
  const { run, calls } = fakeDocker({ health: 'healthy' })
  const imageId = await checkLab(config(), {
    run,

    stableMs: 0
  })
  assert.equal(imageId, id)
  const create = calls.find(args => args[0] === 'container' && args[1] === 'create')
  assert.equal(create.at(-1), id)
  assert.ok(create.includes('--memory'))
  assert.ok(calls.some(args => args.includes('--internal')))
  assert.ok(!JSON.stringify(calls).includes('not-for-output'))
  await assert.rejects(readFile(create[create.indexOf('--env-file') + 1]), /ENOENT/)
  assert.equal(calls.at(-2)[1], 'rm')
  assert.equal(calls.at(-1)[0], 'network')
  const published = await publishLab(
    { directory: 'demo', ...config() },
    { run, owner: 'example', revision, imageId }
  )
  assert.match(published.digest, /@sha256:/)
  const pushes = calls.filter(args => args[1] === 'push')
  assert.deepEqual(
    pushes.map(args => args[2]),
    [`ghcr.io/example/demo:latest-sha-${revision}`, 'ghcr.io/example/demo:latest']
  )
})

test('unhealthy, stopped, unready healthcheck and create failures clean up without pushing', async () => {
  for (const options of [
    { health: 'unhealthy' },
    { running: false },
    { health: 'starting' },
    { failCreate: true }
  ]) {
    const { run, calls } = fakeDocker(options)
    await assert.rejects(
      checkLab(config(), {
        run,

        timeoutMs: 5,
        stableMs: 0
      })
    )
    assert.ok(calls.some(args => args[0] === 'network' && args[1] === 'rm'))
    assert.equal(
      calls.some(args => args[1] === 'push'),
      false
    )
    if (!options.failCreate)
      assert.ok(calls.some(args => args[0] === 'container' && args[1] === 'rm'))
  }
})

test('abort cleans up and publish refuses a missing tested ID', async () => {
  const { run: fake, calls } = fakeDocker({ health: 'starting' })
  const abort = new AbortController()
  await assert.rejects(
    checkLab(config(), {
      run: async args => {
        const result = await fake(args)
        if (args[1] === 'inspect' && args[0] === 'container') abort.abort()
        return result
      },
      signal: abort.signal
    })
  )
  assert.equal(calls.at(-1)[1], 'rm')
  await assert.rejects(publishLab(config(), { run: fake, owner: 'example', revision }), /镜像 ID/)
})

test('workflow publishes only after successful check and keeps build inputs declarative', async () => {
  // Copied content repositories need no other AttackBox source files.
  const workflowFile = new URL('../../.github/workflows/lab-images.yml', import.meta.url)
  let source
  try {
    source = await readFile(workflowFile, 'utf8')
  } catch (error) {
    if (error.code === 'ENOENT') return
    throw error
  }
  const workflow = parse(source)
  const steps = workflow.jobs.publish.steps
  const build = steps.find(step => step.uses?.startsWith('docker/build-push-action'))
  assert.equal(build.with.push, false)
  assert.equal(build.with.load, true)
  assert.equal(workflow.jobs.plan.steps[0].with.ref, 'main')
  assert.equal(steps[0].with.ref, '${{ needs.plan.outputs.revision }}')
  const check = steps.findIndex(step => step.id === 'check')
  const publish = steps.findIndex(step => step.run?.includes('cli.mjs publish'))
  assert.ok(check >= 0 && publish > check)
  assert.ok(!steps[publish].if?.includes('always'))
  assert.match(
    workflow.jobs.plan.steps.find(step => step.id === 'baseline').run,
    /event=push&status=success/
  )
})

test(
  'real Docker: verifies image health without port mappings and removes test resources',
  { skip: !process.env.LAB_DOCKER_TEST, timeout: 120000 },
  async t => {
    const root = await mkdtemp(path.join(tmpdir(), 'lab-real-docker-'))
    const image = `attackbox-publisher-test:${process.pid}`
    t.after(async () => {
      await runDocker(['image', 'rm', '--force', image])
      await rm(root, { recursive: true, force: true })
    })
    await writeFile(
      path.join(root, 'Dockerfile'),
      'FROM nginx:1.27-alpine\nHEALTHCHECK --interval=1s --timeout=1s CMD test -f /etc/nginx/nginx.conf\n'
    )
    await runDocker(['build', '--tag', image, root])
    const lab = validateLabConfig({
      image,
      limits: { memory: 128, cpu: 0.5, pids: 64 }
    })
    assert.match(await checkLab(lab, { timeoutMs: 15000 }), /^sha256:/)
    assert.equal(
      await runDocker([
        'container',
        'ls',
        '--all',
        '--filter',
        'name=attackbox-check-',
        '--format',
        '{{.Names}}'
      ]),
      ''
    )
    assert.equal(
      await runDocker([
        'network',
        'ls',
        '--filter',
        'name=attackbox-check-',
        '--format',
        '{{.Name}}'
      ]),
      ''
    )
  }
)
