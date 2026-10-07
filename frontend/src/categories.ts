// catalogue.garment_type has 22 inconsistent spellings; group them into shop categories.

export const CATEGORIES = [
  { id: 'tees', label: 'T-Shirts & Tops' },
  { id: 'crewnecks', label: 'Crewnecks' },
  { id: 'hoodies', label: 'Hoodies' },
  { id: 'quarter-zips', label: 'Quarter-Zips' },
  { id: 'outerwear', label: 'Jackets & Fleece' },
] as const

export type CategoryId = (typeof CATEGORIES)[number]['id']

export function categoryOf(garmentType: string): CategoryId {
  const type = garmentType.toLowerCase()
  if (type.includes('quarter-zip')) return 'quarter-zips'
  if (type.includes('jacket')) return 'outerwear'
  if (type.includes('hood')) return 'hoodies'
  if (type.includes('crewneck') || type.includes('mockneck')) return 'crewnecks'
  return 'tees'
}
