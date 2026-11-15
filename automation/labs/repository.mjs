import { createHash } from 'node:crypto'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { lstat, readFile, readdir, realpath } from 'node:fs/promises'
import path from 'node:path'
import { parseDocument } from 'yaml'
import { validateLabConfig } from './lab-spec.mjs'

const exec = promisify(execFile)
const declarationNames = ['lab.yml', 'lab.yaml']
const inside = (parent, child) => child === parent || child.startsWith(`${parent}${path.sep}`)

export async function loadLab(root, directory) {
  root = await realpath(root)
  const absolute = await realpath(path.resolve(root, directory))
  if (!inside(root, absolute)) throw new Error('靶机目录必须位于仓库内')
  const names = await readdir(absolute)
  const declarations = declarationNames.filter(name => names.includes(name))
  if (declarations.length !== 1) throw new Error(`${directory}: 只保留一个 lab.yml 或 lab.yaml`)
  for (const name of [declarations[0], 'Dockerfile']) {
    const info = await lstat(path.join(absolute, name))
    if (!info.isFile()) throw new Error(`${directory}/${name}: 必须为普通文件`)
    if (name !== 'Dockerfile' && info.size > 65536)
      throw new Error(`${directory}/${name}: 超过 64 KiB`)
  }
  const text = await readFile(path.join(absolute, declarations[0]), 'utf8')
  const doc = parseDocument(text, {
    uniqueKeys: true,
    merge: false,
    logLevel: 'silent'
  })
  if (doc.errors.length || doc.warnings.length)
    throw new Error(`${directory}: YAML 格式错误或存在重复字段`)
  let raw
  try {
    raw = doc.toJS({ maxAliasCount: 0 })
  } catch {
    throw new Error(`${directory}: 不支持 YAML 别名`)
  }
  try {
    return {
      directory: path.relative(root, absolute).split(path.sep).join('/') || '.',
      ...validateLabConfig(raw)
    }
  } catch (error) {
    throw new Error(`${directory}: ${error.field || 'lab.yml'}: ${error.message}`)
  }
}

// Publishing is stricter than running an existing public image: destination must
// be a tagged GHCR package belonging to the current content repository owner.
export function publication(lab, owner, revision) {
  if (!/^[a-f0-9]{40}$/.test(revision)) throw new Error('必须提供完整的 Git commit SHA')
  const match =
    /^ghcr\.io\/([a-z0-9][a-z0-9-]*)\/([a-z0-9]+(?:[._-][a-z0-9]+)*(?:\/[a-z0-9]+(?:[._-][a-z0-9]+)*)*):([\w][\w.-]{0,127})$/.exec(
      lab.image
    )
  if (!match || match[1] !== owner.toLowerCase()) {
    throw new Error(
      `${lab.directory}: image 必须为 ghcr.io/${owner.toLowerCase()}/<package>:<tag>，不能为 digest`
    )
  }
  if (match[3].length > 83)
    throw new Error(`${lab.directory}: 发布 tag 最多 83 字符，需要为提交后缀保留空间`)
  if (match[3].startsWith('sha-') || /-sha-[a-f0-9]{40}$/.test(match[3]))
    throw new Error(`${lab.directory}: sha- 标签保留给自动发布`)
  const repository = lab.image.slice(0, lab.image.lastIndexOf(':'))
  return {
    directory: lab.directory,
    image: lab.image,
    shaImage: `${repository}:${match[3]}-sha-${revision}`,
    scope: createHash('sha256').update(lab.image).digest('hex').slice(0, 20)
  }
}

async function discover(root, directory = '.') {
  const entries = await readdir(path.join(root, directory), {
    withFileTypes: true
  })
  const names = new Set(entries.map(entry => entry.name))
  const found = []
  if (names.has('Dockerfile') && declarationNames.some(name => names.has(name)))
    found.push(directory)
  for (const entry of entries) {
    if (entry.isDirectory() && !['.git', 'node_modules', 'automation'].includes(entry.name)) {
      found.push(...(await discover(root, path.posix.join(directory, entry.name))))
    }
  }
  return found
}

export async function planLabs({ root, owner, revision, base, directory }) {
  root = await realpath(root)
  const directories = await discover(root)
  const labs = await Promise.all(directories.sort().map(dir => loadLab(root, dir)))
  const entries = labs.map(lab => publication(lab, owner, revision))
  if (new Set(entries.map(entry => entry.scope)).size !== entries.length) {
    throw new Error('不同靶机不能使用相同的完整镜像地址（package 与 tag）')
  }
  let changed
  if (base && !/^0+$/.test(base)) {
    if (!/^[a-f0-9]{40}$/.test(base)) throw new Error('base 必须为完整的 Git commit SHA')
    let exists = true
    try {
      await exec('git', ['cat-file', '-e', `${base}^{commit}`], { cwd: root })
    } catch {
      exists = false
    }
    if (exists) {
      const { stdout } = await exec(
        'git',
        ['diff', '--no-renames', '--name-only', '-z', base, revision],
        { cwd: root, maxBuffer: 16 * 1024 * 1024 }
      )
      changed = stdout.split('\0').filter(Boolean)
    }
  }
  const toolChanged = changed?.some(
    file => file.startsWith('automation/labs/') || file === '.github/workflows/lab-images.yml'
  )
  const selected = entries.filter(entry => {
    if (directory) return entry.directory === directory.replace(/^\.\//, '').replace(/\/$/, '')
    if (!changed || toolChanged) return true
    const prefix = entry.directory === '.' ? '' : `${entry.directory}/`
    return changed.some(file => {
      if (!file.startsWith(prefix)) return false
      const relative = file.slice(prefix.length)
      // Direct Markdown files are the tutorial, not image inputs. Put exercise
      // fixture Markdown under files/ so its edits rebuild the image.
      return relative.includes('/') || !relative.toLowerCase().endsWith('.md')
    })
  })
  if (directory && !selected.length) throw new Error(`未找到可构建靶机目录: ${directory}`)
  if (selected.length > 256)
    throw new Error('单次构建超过 GitHub matrix 的 256 个任务限制，请按目录手动发布')
  return { include: selected }
}
