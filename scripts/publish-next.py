#!/usr/bin/env python3
"""
毎日1本ずつ article_queue.json から記事を取り出し、
articles.json に追記するスクリプト。
GitHub Actions の daily-publish.yml から呼び出される。
"""

import json
import os
import sys

QUEUE_PATH = 'src/data/article_queue.json'
ARTICLES_PATH = 'src/data/articles.json'


def set_output(key, value):
    """GitHub Actions のステップ出力を設定する"""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f'{key}={value}\n')


def main():
    # キューを読み込む
    with open(QUEUE_PATH, 'r', encoding='utf-8') as f:
        queue = json.load(f)

    if not queue:
        print('キューが空です。公開する記事がありません。')
        set_output('article_id', '')
        set_output('article_title', '')
        sys.exit(0)

    # 先頭の記事を取り出す
    article = queue.pop(0)

    # 管理用フィールドを除去
    article.pop('published', None)

    # 既存の articles.json を読み込む
    with open(ARTICLES_PATH, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    # 重複チェック
    existing_ids = {a['id'] for a in articles}
    if article['id'] in existing_ids:
        print(f'記事 {article["id"]} はすでに公開済みです。スキップします。')
        # キューからは除去してファイルを更新
        with open(QUEUE_PATH, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        set_output('article_id', '')
        set_output('article_title', '')
        set_output('queue_updated', 'true')
        sys.exit(0)

    # articles.json の先頭に追加（新しい記事が上に来るように）
    articles.insert(0, article)

    # 両ファイルを書き出す
    with open(ARTICLES_PATH, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    with open(QUEUE_PATH, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    article_id = article['id']
    article_title = article['title'].replace('\n', ' ')

    print(f'公開完了: {article_id}')
    print(f'タイトル: {article_title}')
    print(f'残りキュー: {len(queue)} 本')

    set_output('article_id', article_id)
    set_output('article_title', article_title)


if __name__ == '__main__':
    main()
