import type { CharacterData } from '../types/messages';

export function parseCharacterMarkdown(markdown: string): CharacterData | null {
  try {
    const nameMatch = markdown.match(/^#\s+(.+?)\s+-\s+Level/m);
    const hpMatch = markdown.match(/\*\*Hit Points\*\*\s*\|\s*(\d+)\s*\/\s*(\d+)/);
    const acMatch = markdown.match(/\*\*Armor Class \(AC\)\*\*\s*\|\s*(\d+)/);
    const speedMatch = markdown.match(/\*\*Speed\*\*\s*\|\s*(\d+)/);
    const classMatch = markdown.match(/\*\*Class & Level\*\*\s*\|\s*(.+)/);
    const raceMatch = markdown.match(/\*\*Race\/Species\*\*\s*\|\s*(.+)/);
    const spellMatch = markdown.match(/\*\*1st\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)/);

    return {
      name: nameMatch?.[1]?.trim() ?? 'Unknown',
      classLevel: classMatch?.[1]?.trim() ?? '',
      race: raceMatch?.[1]?.trim() ?? '',
      hp_current: parseInt(hpMatch?.[1] ?? '0'),
      hp_max: parseInt(hpMatch?.[2] ?? '0'),
      ac: parseInt(acMatch?.[1] ?? '0'),
      speed: parseInt(speedMatch?.[1] ?? '0'),
      conditions: [],
      spell_slots_total: parseInt(spellMatch?.[1] ?? '0'),
      spell_slots_used: parseInt(spellMatch?.[2] ?? '0'),
    };
  } catch {
    return null;
  }
}
