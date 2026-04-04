# 【おばあちゃんのレシピ】プロジェクト概要

サイトURL：www.obaachan-recipe.com
構成：Astro 4.x SSG（GitHub Pages）
SNS：@obaachan_recipe（Instagram・Threads・TikTok）

## カテゴリ構成
- レシピ一覧（地域・タグで絞り込み）
- 地域で探す
- 読み物（4カテゴリ）

## 読み物カテゴリ

| カテゴリ | slug | 内容 |
|---|---|---|
| 暮らしのレシピ帖 | `life` | シーン別・悩み別のまとめ＆ガイド |
| 季節の手仕事 | `teshigoto` | 保存食・季節行事・仕込みもの |
| おばあちゃんのストーリー | `story` | 人物・思い出・エピソード |
| 食文化コラム | `column` | 知識・歴史・考察 |

## 記事本文の記法

- `## 見出し` → `<h2>` に変換
- `**太字**` → `<strong>` に変換
- `\n` → `<br>`（段落内改行）
- `\n\n` → 段落区切り
- `---` → `<hr>`
- `{{recipe:レシピID}}` → レシピカードを埋め込み（独立した段落として記述）
  **必ず「カード → 説明文」の順で書くこと。説明文を先に書いてカードを後に置くのはNG。**
- `{{recruit:#おばあちゃんのレシピ}}` → レシピ募集リンク
- タイトル（title）に `\n` を入れると `<br>` として改行表示
- `[テキスト](/パス)` → サイト内リンク
- `[テキスト](https://...)` → 外部リンク（`target="_blank"` 付き）

## articles.json のフィールド

| フィールド | 必須 | 説明 |
|---|---|---|
| `id` | ✓ | URLスラッグ |
| `title` | ✓ | `\n` で改行表示可 |
| `subtitle` | | サブタイトル |
| `lead` | ✓ | リード文。一覧カードや meta description のフォールバック |
| `meta_description` | | SEO用（省略時は lead 先頭120文字） |
| `body` | ✓ | 本文 |
| `faq` | | `[{q,a}]` 配列。FAQPage JSON-LD が自動生成される |
| `tags` | ✓ | タグ配列 |
| `category` | ✓ | 表示用カテゴリ名 |
| `category_slug` | ✓ | `life` / `teshigoto` / `story` / `column` |
| `published_at` | ✓ | `YYYY-MM-DD` |
| `reading_time` | ✓ | 読了目安（分） |
| `thumbnail_emoji` | ✓ | 絵文字1つ |
| `related_recipe_id` | | 記事末尾にボタン表示 |
| `references` | | 参考文献配列 |

## 本文テキストの注意点

- **行末の1文字残しNG**：ぶら下がりは絶対に避ける
  - CSS で `word-break: auto-phrase; overflow-wrap: anywhere; text-wrap: pretty;` 適用済み
  - `word-break: auto-phrase` はChrome限定。`text-wrap: pretty` の方が対応広め
  - **一番確実な対策は `\n` を入れて自然な位置で改行すること**

## 材料表記ルール（approx_weight）

### 基本ルール
- 「本・個・枚・丁・片」など生活単位の食材には `approx_weight` フィールドで目安グラム数を追加
- 形式: `"approx_weight": "150〜180g"` のように幅を持たせた表記を推奨
- 表示: 「⚖️ きっちり計量」モードで amount の後ろに `（約◯g）` として表示
- JSON-LD（構造化データ）にも反映済み

### 対象・対象外
- **対象**: 野菜・肉・豆腐など個体差のある食材
- **対象外**: 卵、調味料、パッケージ品（袋入り等）、少量の薬味（鷹の爪等）、すでにg/cc単位のもの

### 禁止事項
- すべてg表記に統一すること（世界観を壊さない）
- 不自然な分量の設定
- 補足文: 材料セクションに「※おばあちゃんのレシピでは『だいたいこのくらい』で…」を表示済み

### approx_weight 目安グラム数

| 食材 | 目安 |
|---|---|
| 大根 1本 | 約800g〜1kg |
| 大根 1/2本 | 約400〜500g |
| 人参 1本 | 約150〜180g |
| じゃがいも 1個 | 約150g |
| 玉ねぎ 1個 | 約200g |
| 里芋 1個 | 約40〜60g |
| ごぼう 1本 | 約150〜180g |
| れんこん 1節 | 約150〜200g |
| 白菜 1/4株 | 約500g |
| キャベツ 1/4個 | 約250〜300g |
| なす 1本 | 約80〜100g |
| きゅうり 1本 | 約100g |
| 長ねぎ 1本 | 約100g |
| しいたけ 1枚 | 約15〜20g |
| こんにゃく 1枚 | 約250g |
| 豆腐 1丁 | 約300〜400g |
| 油揚げ 1枚 | 約30g |
| しょうが 1片 | 約10〜15g |
| にんにく 1片 | 約5〜8g |

## データファイルの同期手順

SOURCE（常にここを編集）：`/Users/aoi/Desktop/obaachan-recipe/data/articles.json`
ASTRO（コピー先）：`/Users/aoi/Desktop/obaachan-recipe-astro/src/data/articles.json`

```bash
cp -f /Users/aoi/Desktop/obaachan-recipe/data/articles.json \
       /Users/aoi/Desktop/obaachan-recipe-astro/src/data/articles.json

diff ... && echo "同期OK"
```

- `git diff` の変更行数が想定より少ない場合は同期漏れを疑う
- 他のコミットが Astro 側を上書きしていないか確認する

## 作業ルール

- **レシピ追加は必ず `obaachan-recipe-astro/` 内で行う**（v2〜v5等の別ディレクトリは使わない）
- **レシピをrecipes.jsonに追加したら都度コミットする**（セッション切れでデータを失わないため）
- デプロイ（push）はすべてのレシピ追加が終わってからまとめてでOK
- **レシピ追加時の必須チェック:**
  - `category` は既存値のいずれかを使う: 汁物 / 主菜 / 煮物 / 揚げ物 / 副菜 / 佃煮・常備菜 / 和え物・酢の物 / 漬物 / ご飯もの / おやつ / 和菓子・甘味
  - `view_count` フィールドを必ず含める（新規は `0`）
  - `tags` に COMMON_TAGS（煮物/日常のごはん/お正月/郷土料理/山菜/家庭料理/常備菜/保存食/和え物/春の味覚）のうち最低1つを含める
  - `region.area` が正しいエリアコード（hokkaido/tohoku/kanto/hokuriku/koshinetsu/tokai/kinki/chugoku/shikoku/kyushu）であること
  - `grandmother.name` に投稿者名を設定する（匿名希望の場合はnullでOK → 「○○県のおばあちゃん」としてカウントされる）
  - `grandmother.prefecture` が設定されていること（ティッカーの「つながった土地」「出会ったおばあちゃん」に反映される）
  - `source` フィールドは `{"types": ["..."], "contributor": "投稿者名"}` 形式にすること（⚠️ `type`/`details` はNG。テンプレートが `source.types.map()` で参照するため、形式が違うとビルドエラーになる）
    - `types`: 情報源の配列（例: `["おばあちゃん本人から直接教わった", "記憶を頼りに書いている"]`）
    - `contributor`: 投稿者のニックネーム（例: `"トラネコ"`）
- **push前に必ず `npm run build` でローカルビルドを実行する**（CI失敗を防ぐため）

## デプロイ確認手順

- Actions 成功でも必ず `curl` で本番を確認する
- ブラウザキャッシュが残ることがある → `Cmd+Shift+R` で強制リロード

## 日次自動公開システム

- `src/data/article_queue.json` にキューを保持、毎日1本ずつ自動公開
- スクリプト：`scripts/publish-next.py`
- ワークフロー：`.github/workflows/daily-publish.yml`（毎日 08:00 JST）
- publish → build → deploy を1ワークフローに統合（GITHUB_TOKEN の push は他 workflow をトリガーしないため）
- リポジトリの Actions 権限は `write` に設定済み
