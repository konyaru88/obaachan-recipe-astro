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
- タイトル（title）に `\n` を入れると `<br>` として改行表示
- `[テキスト](/パス)` → サイト内リンク（`##`/`###` 見出し内でも変換される）
- `[テキスト](https://...)` → 外部リンク（`target="_blank"` 付き）
- ⚠️ `{{recruit:}}` は使用禁止

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
| `tags` | ✓ | タグ配列（下記「記事タグのルール」参照） |
| `category` | ✓ | 表示用カテゴリ名 |
| `category_slug` | ✓ | `life` / `teshigoto` / `story` / `column` |
| `published_at` | ✓ | `YYYY-MM-DD` |
| `reading_time` | ✓ | 読了目安（分） |
| `thumbnail_emoji` | ✓ | 絵文字1つ |
| `related_recipe_id` | | 記事末尾にボタン表示 |
| `references` | | 参考文献配列 |

## 記事タグのルール

タグはサイト内回遊のためのリンク。リンク先が存在する値のみ使用すること。

**使用可能なタグ値：**
- レシピのCOMMON_TAGS → `/recipes/?tag=X` にリンク
  煮物 / 日常のごはん / お正月 / 郷土料理 / 山菜 / 家庭料理 / 常備菜 / 保存食 / 和え物 / 春の味覚
- 地域名 → `/region/{code}/` にリンク
  北海道 / 東北 / 関東 / 北陸 / 甲信越 / 東海 / 近畿 / 中国 / 四国 / 九州

**禁止：** リンク先のない独自タグ（回遊性がないため意味がない）
**マッピングロジック：** `src/pages/articles/[id].astro` の `tagToUrl()`

## 本文テキストの注意点

- **行末の1文字残しNG**：ぶら下がりは絶対に避ける
  - CSS で `word-break: auto-phrase; overflow-wrap: anywhere; text-wrap: pretty;` 適用済み
  - `word-break: auto-phrase` はChrome限定。`text-wrap: pretty` の方が対応広め
  - **一番確実な対策は `\n` を入れて自然な位置で改行すること**

## エピソード品質ルール

- **最低3文以上**：エピソード（`episode`）や思い出セクションは最低3文以上にする。1文だけのエピソードは薄すぎるため不可
- **五感の描写を入れる**：音・匂い・温度・触感など、記憶を呼び起こす描写を最低1つ含める
- **具体的なエピソード**：「おいしかった」のような抽象的な感想ではなく、具体的な場面・会話・状況を書く
- 良い例：台所の暑さ、方言での注意、食卓の配置、季節の情景
- 悪い例：「おばあちゃんの味でした」「懐かしい味です」

## トーン統一ガイドライン（おばあちゃんの語り口）

- **調理手順は「だいたい」を基本にする**：「45秒加熱」ではなく「1分くらい」、「180度で12分」ではなく「こんがりするまで」
- **方言・口癖があれば活かす**：投稿者から聞いた言い回しはそのまま残す（東北弁、関西弁など）
- **レシピブログ調にしない**：「えぐみが取れる」「全体に味がなじんだら」のような洗練された表現は避け、「苦いのが抜ける」「味がしみたら」のような日常語を使う
- **精度の統一**：グラム数は材料欄（`amount`）に書き、手順文中では「大さじ」「ひとつまみ」「だいたいこのくらい」を使う
- **トーンの基準はきんぴらごぼう（宮城県）ページ**：方言と生活感が自然に入った理想的なトーン

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
- **レシピ追加後の同期確認（ビルド時に自動計算されるが、入力値が正しくないと反映されない）:**
  - レシピ一覧の件数が増えているか（`allRecipes.length` で自動計算）
  - 地方フィルター: `region.area` が正しければ自動で絞り込み対象になる
  - タグフィルター: `tags` に COMMON_TAGS が含まれていれば自動でヒットする
  - トップページのハッシュタグ（#コトコト煮物おばあちゃん等）: tags配列のマッチで自動連動
  - ティッカー「つながった土地：X県」: `grandmother.prefecture` の重複排除カウント。新しい県が増える場合は数値が変わる
  - 日本地図ヒートマップ: `region.area` で自動集計
- **画像なしレシピ**: `photos: []` にすれば準備中画像（`sample-placeholder.png.jpg`）が自動表示される
- **push前に必ず `npm run build` でローカルビルドを実行する**（CI失敗を防ぐため）

## CrowdWorks CSVからのレシピ取り込み

- CSVのエンコーディングは **cp932**（Shift_JIS系）。`iconv` では失敗することがあるので、Pythonの `open(file, 'rb').read().decode('cp932')` を使う
- **既存レシピとの重複チェック必須**: 料理名＋都道府県で突き合わせて、新規分のみ取り込む
- CSVカラム構造:
  | Col | 内容 |
  |---|---|
  | 4 | 料理名 |
  | 5 | 地域（都道府県） |
  | 6 | いつ頃よく作っていたか |
  | 7 | どんな場面で食べていたか |
  | 8 | 材料と分量（おばあちゃん流＋きっちり） |
  | 9 | 作り方・手順 |
  | 10-19 | 情報源（複数カラムに分散） |
  | 20 | エピソード |
  | 21 | ニックネーム |
- 情報源の変換ルール: `1`=「おばあちゃん本人から直接教わった」、`2`=「家族（親・きょうだいなど）から聞いた」、`4`=「記憶を頼りに書いている」
- 材料テキストは自由記述なので、`grandma_amount` と `amount` を手動で分離してJSON化する必要がある

## デプロイ確認手順

- Actions 成功でも必ず `curl` で本番を確認する
- ブラウザキャッシュが残ることがある → `Cmd+Shift+R` で強制リロード

## 週次閲覧数更新システム（view_count）

- GA4 Data API で `/recipes/xxx/` のページビュー数を取得 → recipes.json の `view_count` を更新
- スクリプト：`scripts/update-view-counts.py`
- ワークフロー：`.github/workflows/weekly-view-counts.yml`（毎週月曜 06:00 JST）
- 手動実行も可（GitHub Actions → Weekly View Count Update → Run workflow）
- 変更がある場合のみ commit → build → deploy（変更なしならスキップ）
- GA4認証: サービスアカウント `ga4-reader@obaachan-recipe.iam.gserviceaccount.com`
- GitHub Secret: `GA4_CREDENTIALS_JSON`（サービスアカウントのJSON鍵）
- Google Cloud プロジェクト: `obaachan-recipe`（Analytics Data API 有効化済み）
- GA4プロパティID: `529409641`
- `view_count` はレシピ一覧の「人気順」ソートに使用（クライアントサイドJS）

## 日次自動公開システム

- `src/data/article_queue.json` にキューを保持、毎日1本ずつ自動公開
- スクリプト：`scripts/publish-next.py`
- ワークフロー：`.github/workflows/daily-publish.yml`（毎日 08:00 JST）
- publish → build → deploy を1ワークフローに統合（GITHUB_TOKEN の push は他 workflow をトリガーしないため）
- リポジトリの Actions 権限は `write` に設定済み
