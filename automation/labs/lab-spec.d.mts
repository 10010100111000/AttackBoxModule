export interface LabResources {
  memoryMB: number
  cpus: number
  pidsLimit: number
}
export interface LabConfig {
  name: string
  summary: string
  image: string
  entryPort: number
  resources: LabResources
  variables: Record<string, string>
  variableKeys: string[]
  accessInstructions: string
}
export class LabSpecError extends Error {
  constructor(field: string, message: string)
  field: string
}
export const DEFAULT_TARGET_RESOURCES: Readonly<LabResources>
export function validateLabConfig(raw: unknown, defaultName?: string): LabConfig
