export const moduleKeys = [
  'indicators',
  'measurements',
  'reports',
  'chamados',
  'fotos',
] as const;

export type ModuleKey = (typeof moduleKeys)[number];

export function isModuleKey(
  value: unknown,
): value is ModuleKey {
  return (
    typeof value === 'string'
    && moduleKeys.includes(value as ModuleKey)
  );
}