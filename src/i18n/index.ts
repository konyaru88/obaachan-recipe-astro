import { ui, type UiKey } from './ui';

export type Lang = 'ja' | 'en';
export const defaultLang: Lang = 'ja';
export const languages = { ja: '日本語', en: 'English' } as const;

export function getLangFromUrl(url: URL): Lang {
  const seg = url.pathname.split('/')[1];
  return seg === 'en' ? 'en' : 'ja';
}

export function t(lang: Lang, key: UiKey): string {
  return ui[lang][key] ?? ui.ja[key] ?? key;
}

/** Build a locale-aware path. ja keeps bare path, en prepends /en */
export function localePath(lang: Lang, path: string): string {
  if (lang === 'ja') return path;
  // avoid double /en/
  const clean = path.startsWith('/en/') ? path.slice(3) : path;
  return `/en${clean}`;
}

/** Swap between languages for the same page */
export function alternatePath(lang: Lang, currentPath: string): string {
  if (lang === 'en') {
    // currently EN → switch to JA
    return currentPath.replace(/^\/en(\/|$)/, '/');
  }
  // currently JA → switch to EN
  return `/en${currentPath}`;
}

export function formatTime(minutes: number, lang: Lang): string {
  if (!minutes) return '-';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (lang === 'en') {
    if (h > 0 && m > 0) return `${h}h ${m}min`;
    if (h > 0) return `${h}h`;
    return `${m}min`;
  }
  if (h > 0 && m > 0) return `${h}時間${m}分`;
  if (h > 0) return `${h}時間`;
  return `${m}分`;
}

export function formatServings(n: number, lang: Lang): string {
  return lang === 'en' ? `${n} servings` : `${n}人分`;
}

/** Area code → localized label */
export function areaLabel(code: string, lang: Lang): string {
  const key = `area.${code}` as UiKey;
  return t(lang, key);
}

/** Category key for English display */
const CATEGORY_EN: Record<string, string> = {
  '汁物': 'Soups',
  '主菜': 'Main Dishes',
  '煮物': 'Simmered Dishes',
  '揚げ物': 'Fried Dishes',
  '副菜': 'Side Dishes',
  '佃煮・常備菜': 'Preserved & Pantry',
  '和え物・酢の物': 'Dressed & Vinegared',
  '漬物': 'Pickles',
  'ご飯もの': 'Rice Dishes',
  'おやつ': 'Snacks & Sweets',
  '和菓子・甘味': 'Japanese Sweets',
};

export function categoryLabel(ja: string, lang: Lang): string {
  if (lang === 'ja') return ja;
  return CATEGORY_EN[ja] ?? ja;
}

/** Common tags mapping */
const COMMON_TAGS_EN: Record<string, string> = {
  '煮物': 'Simmered',
  '日常のごはん': 'Everyday',
  'お正月': 'New Year',
  '郷土料理': 'Regional',
  '山菜': 'Wild Plants',
  '家庭料理': 'Home Cooking',
  '常備菜': 'Make-Ahead',
  '保存食': 'Preserved',
  '和え物': 'Dressed',
  '春の味覚': 'Spring',
};

export function tagLabel(ja: string, lang: Lang): string {
  if (lang === 'ja') return ja;
  return COMMON_TAGS_EN[ja] ?? ja;
}
