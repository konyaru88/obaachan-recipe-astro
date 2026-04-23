-- ========================================================================
-- みんなの食卓ボード schema
-- Supabase SQL Editor で上から順に実行する
-- ========================================================================

-- 1) posts テーブル
create table if not exists posts (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),

  type        text not null check (type in ('quick','recipe','memory')),
  nickname    text not null,
  region      text,

  -- quick
  text        text,

  -- recipe
  recipe_name text,
  ingredients text,
  steps       text,
  episode     text,

  -- memory
  memory_name text,
  memory      text,
  clue        text,

  -- meta
  likes_count int not null default 0,
  is_hidden   boolean not null default false,
  uid         text  -- ブラウザID（編集・削除権限用）
);

create index if not exists posts_created_at_desc
  on posts (created_at desc)
  where is_hidden = false;

-- 2) Row Level Security
alter table posts enable row level security;

-- 公開読み取り: is_hidden=false のみ
drop policy if exists "read public posts" on posts;
create policy "read public posts" on posts
  for select
  using (is_hidden = false);

-- 投稿（INSERT）: nickname / type / 長さ制限のみチェック
drop policy if exists "anyone can insert" on posts;
create policy "anyone can insert" on posts
  for insert
  with check (
    nickname is not null
    and length(nickname) between 1 and 50
    and type in ('quick','recipe','memory')
    and (text        is null or length(text)        <= 2000)
    and (ingredients is null or length(ingredients) <= 2000)
    and (steps       is null or length(steps)       <= 4000)
    and (episode     is null or length(episode)     <= 2000)
    and (memory      is null or length(memory)      <= 2000)
    and (clue        is null or length(clue)        <= 1000)
    and (recipe_name is null or length(recipe_name) <= 100)
    and (memory_name is null or length(memory_name) <= 100)
    and (region      is null or length(region)      <= 20)
    and is_hidden = false   -- クライアントが勝手に is_hidden を指定できない
  );

-- UPDATE / DELETE は RLS で全拒否。RPC 関数経由でのみ行う
-- （直接 anon で update/delete ができないように）

-- ========================================================================
-- RPC 関数（security definer で実行）
-- ========================================================================

-- いいね（1カウント増やす）
create or replace function like_post(p_id uuid)
returns int
language plpgsql
security definer
set search_path = public
as $$
declare
  new_count int;
begin
  update posts
     set likes_count = likes_count + 1
   where id = p_id and is_hidden = false
   returning likes_count into new_count;
  if new_count is null then
    raise exception 'post not found';
  end if;
  return new_count;
end;
$$;

-- いいね取り消し
create or replace function unlike_post(p_id uuid)
returns int
language plpgsql
security definer
set search_path = public
as $$
declare
  new_count int;
begin
  update posts
     set likes_count = greatest(likes_count - 1, 0)
   where id = p_id and is_hidden = false
   returning likes_count into new_count;
  if new_count is null then
    raise exception 'post not found';
  end if;
  return new_count;
end;
$$;

-- 自分の投稿削除（uid 一致のみ）
create or replace function delete_my_post(p_id uuid, p_uid text)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  delete from posts where id = p_id and uid = p_uid;
end;
$$;

-- 自分の投稿編集（uid 一致のみ、渡した値だけ上書き）
create or replace function update_my_post(
  p_id           uuid,
  p_uid          text,
  p_nickname     text default null,
  p_region       text default null,
  p_text         text default null,
  p_recipe_name  text default null,
  p_ingredients  text default null,
  p_steps        text default null,
  p_episode      text default null,
  p_memory_name  text default null,
  p_memory       text default null,
  p_clue         text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  update posts set
    nickname    = coalesce(p_nickname,    nickname),
    region      = coalesce(p_region,      region),
    text        = coalesce(p_text,        text),
    recipe_name = coalesce(p_recipe_name, recipe_name),
    ingredients = coalesce(p_ingredients, ingredients),
    steps       = coalesce(p_steps,       steps),
    episode     = coalesce(p_episode,     episode),
    memory_name = coalesce(p_memory_name, memory_name),
    memory      = coalesce(p_memory,      memory),
    clue        = coalesce(p_clue,        clue),
    updated_at  = now()
   where id = p_id and uid = p_uid and is_hidden = false;
end;
$$;

-- RPC 関数を anon から呼べるように grant
grant execute on function like_post(uuid)       to anon, authenticated;
grant execute on function unlike_post(uuid)     to anon, authenticated;
grant execute on function delete_my_post(uuid, text) to anon, authenticated;
grant execute on function update_my_post(uuid, text, text, text, text, text, text, text, text, text, text, text) to anon, authenticated;
