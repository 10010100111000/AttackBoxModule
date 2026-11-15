// The author-facing lab.yml contract shared by Control and the portable publisher.
export const DEFAULT_TARGET_RESOURCES = Object.freeze({
  memoryMB: 512,
  cpus: 1,
  pidsLimit: 256
})

const ALLOWED_LAB_KEYS = new Set(['image', 'env', 'limits'])
const ALLOWED_RESOURCE_KEYS = new Set(['memory', 'cpu', 'pids'])
const IMAGE_REF_PATTERN =
  /^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*(?::[0-9]{2,5})?(?:\/[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*)*(?::[A-Za-z0-9_][A-Za-z0-9._-]{0,127})?(?:@sha256:[a-f0-9]{64})?$/i
const ENV_KEY_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/

export class LabSpecError extends Error {
  constructor(field, message) {
    super(message)
    this.name = 'LabSpecError'
    this.field = field
  }
}

function fail(field, message) {
  throw new LabSpecError(field, message)
}

function validateContainerImageRef(image) {
  if (typeof image !== 'string') {
    fail('image', '必须声明单容器镜像地址 image（如 ghcr.io/org/lab:1.0.0）')
  }
  const trimmed = image.trim()
  if (
    !trimmed ||
    trimmed.length > 500 ||
    trimmed.startsWith('-') ||
    /\s/.test(trimmed) ||
    !IMAGE_REF_PATTERN.test(trimmed)
  ) {
    fail(
      'image',
      '镜像地址格式无效（支持如 ghcr.io/org/lab:1.0.0 或 @sha256:...，长度不超过 500 字符）'
    )
  }
  return trimmed
}

function validateTargetResources(raw) {
  if (raw === undefined || raw === null) {
    return { ...DEFAULT_TARGET_RESOURCES }
  }
  if (typeof raw !== 'object' || Array.isArray(raw)) {
    fail('limits', 'limits 必须为包含 memory、cpu、pids 的对象')
  }
  const obj = raw
  for (const k of Object.keys(obj)) {
    if (!ALLOWED_RESOURCE_KEYS.has(k)) {
      fail(`limits.${k}`, `不支持的资源限制字段: ${k}`)
    }
  }
  const memoryMB = obj.memory === undefined ? DEFAULT_TARGET_RESOURCES.memoryMB : Number(obj.memory)
  if (!Number.isInteger(memoryMB) || memoryMB < 64 || memoryMB > 8192) {
    fail('limits.memory', 'memory（MiB）必须为 64–8192 之间的整数')
  }
  const cpus = obj.cpu === undefined ? DEFAULT_TARGET_RESOURCES.cpus : Number(obj.cpu)
  if (!Number.isFinite(cpus) || cpus < 0.25 || cpus > 8) {
    fail('limits.cpu', 'cpu 必须为 0.25–8.0 之间的数值')
  }
  const pidsLimit = obj.pids === undefined ? DEFAULT_TARGET_RESOURCES.pidsLimit : Number(obj.pids)
  if (!Number.isInteger(pidsLimit) || pidsLimit < 32 || pidsLimit > 4096) {
    fail('limits.pids', 'pids 必须为 32–4096 之间的整数')
  }
  return { memoryMB, cpus, pidsLimit }
}

export function validateLabConfig(labObj) {
  if (!labObj || typeof labObj !== 'object' || Array.isArray(labObj)) {
    fail('', 'lab.yml 必须为键值映射对象')
  }
  for (const key of Object.keys(labObj)) {
    if (!ALLOWED_LAB_KEYS.has(key)) {
      fail(key, `lab.yml 包含不支持的字段: ${key}`)
    }
  }

  const image = validateContainerImageRef(labObj.image)

  const resources = validateTargetResources(labObj.limits)

  const rawEnv = labObj.env
  const variables = Object.create(null)
  if (rawEnv !== undefined && rawEnv !== null) {
    if (typeof rawEnv !== 'object' || Array.isArray(rawEnv)) {
      fail('env', 'env 必须为键值映射对象')
    }
    const varEntries = Object.entries(rawEnv)
    if (varEntries.length > 64) {
      fail('env', 'env 最多支持 64 个环境变量')
    }
    for (const [k, v] of varEntries) {
      if (!ENV_KEY_PATTERN.test(k)) {
        fail(`env.${k}`, `无效的环境变量名: ${k}`)
      }
      const strVal =
        typeof v === 'string'
          ? v
          : typeof v === 'number' || typeof v === 'boolean'
            ? String(v)
            : null
      if (strVal === null || strVal.length === 0 || strVal.length > 8192) {
        fail(`env.${k}`, `环境变量 "${k}" 的值必须为 1–8192 字符的非空文本`)
      }
      variables[k] = strVal
    }
  }

  const orderedVariables = Object.fromEntries(
    Object.entries(variables).sort(([a], [b]) => a.localeCompare(b))
  )
  if (new TextEncoder().encode(JSON.stringify(orderedVariables)).length > 32768) {
    fail('env', 'env 变量总字节长度不能超过 32 KiB')
  }

  return {
    image,
    resources,
    variables: orderedVariables
  }
}
