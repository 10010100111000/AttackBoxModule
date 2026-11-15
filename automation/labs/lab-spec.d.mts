export interface LabResources {
  memoryMB: number
  cpus: number
  pidsLimit: number
}
export interface LabConfig {
  image: string
  resources: LabResources
  variables: Record<string, string>
}
export class LabSpecError extends Error {
  constructor(field: string, message: string)
  field: string
}
export const DEFAULT_TARGET_RESOURCES: Readonly<LabResources>
export function validateLabConfig(raw: unknown): LabConfig
