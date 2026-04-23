import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  // ビルド時に警告するためのメッセージ。実行時に例外にはしない。
  console.warn('[supabase] PUBLIC_SUPABASE_URL / PUBLIC_SUPABASE_ANON_KEY が未設定です');
}

export const supabase = createClient(supabaseUrl ?? '', supabaseAnonKey ?? '', {
  auth: { persistSession: false },
});

export type PostType = 'quick' | 'recipe' | 'memory';

export interface Post {
  id: string;
  created_at: string;
  updated_at: string;
  type: PostType;
  nickname: string;
  region: string | null;
  text: string | null;
  recipe_name: string | null;
  ingredients: string | null;
  steps: string | null;
  episode: string | null;
  memory_name: string | null;
  memory: string | null;
  clue: string | null;
  likes_count: number;
  is_hidden: boolean;
  uid: string | null;
}
