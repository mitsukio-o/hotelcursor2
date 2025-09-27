#!/bin/bash

# ホテル返信システム デプロイスクリプト

set -e

echo "🏨 ホテル返信システムのデプロイを開始します..."

# 環境変数ファイルの確認
if [ ! -f .env ]; then
    echo "⚠️  .envファイルが見つかりません。.env.exampleをコピーして設定してください。"
    cp .env.example .env
    echo "📝 .envファイルを作成しました。必要なAPIキーを設定してください。"
    exit 1
fi

# Docker Composeの確認
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Composeがインストールされていません。"
    echo "Docker Composeをインストールしてから再実行してください。"
    exit 1
fi

# 既存のコンテナを停止・削除
echo "🛑 既存のコンテナを停止中..."
docker-compose down --remove-orphans

# イメージを再ビルド
echo "🔨 Dockerイメージをビルド中..."
docker-compose build --no-cache

# データベースとRedisを起動
echo "🗄️  データベースとRedisを起動中..."
docker-compose up -d postgres redis

# データベースの起動を待機
echo "⏳ データベースの起動を待機中..."
sleep 10

# データベーステーブルを作成
echo "📊 データベーステーブルを作成中..."
docker-compose run --rm api python -c "from app.database import create_tables; create_tables()"

# サンプルデータを投入
echo "🌱 サンプルデータを投入中..."
docker-compose run --rm api python app/seed_data.py

# 全サービスを起動
echo "🚀 全サービスを起動中..."
docker-compose up -d

# サービスの起動を待機
echo "⏳ サービスの起動を待機中..."
sleep 15

# ヘルスチェック
echo "🔍 ヘルスチェックを実行中..."

# FastAPIのヘルスチェック
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPIサービスが正常に起動しました"
else
    echo "❌ FastAPIサービスの起動に失敗しました"
    docker-compose logs api
    exit 1
fi

# Streamlitのヘルスチェック
if curl -f http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Streamlitサービスが正常に起動しました"
else
    echo "❌ Streamlitサービスの起動に失敗しました"
    docker-compose logs streamlit
    exit 1
fi

echo ""
echo "🎉 デプロイが完了しました！"
echo ""
echo "📱 アクセスURL:"
echo "   - Streamlit UI: http://localhost:8501"
echo "   - FastAPI Docs: http://localhost:8000/docs"
echo "   - API Health: http://localhost:8000/health"
echo ""
echo "📋 次のステップ:"
echo "   1. Streamlit UIにアクセスしてホテルを登録"
echo "   2. メッセージ管理タブで新しいメッセージを取得"
echo "   3. 返信候補を生成して返信を送信"
echo ""
echo "🔧 管理コマンド:"
echo "   - ログ確認: docker-compose logs -f"
echo "   - サービス停止: docker-compose down"
echo "   - サービス再起動: docker-compose restart"
echo ""

# サービスの状態を表示
echo "📊 サービス状態:"
docker-compose ps