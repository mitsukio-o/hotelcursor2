# ホテル向け自動返信システム

Booking.comやAirbnbなどのプラットフォームからのゲストメッセージに対して、AIを活用した自動返信候補を生成し、ワンクリックで返信できるシステムです。

## ⚡ 5分で始める

```bash
# 1. 環境変数を設定
cp .env.example .env
# .envファイルでAPIキーを設定（OpenAI APIキーとGoogle Maps APIキー）

# 2. ワンクリックデプロイ
./deploy.sh

# 3. アクセス
# Web UI: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

**APIキーなしでも動作します**（モックデータを使用）

📖 [詳細な実行例とデモ画面はこちら](EXAMPLES.md)

## 機能

### 主要機能
- **マルチエージェントシステム**: ホテル周辺情報検索エージェントと予約データ学習エージェント
- **自動返信候補生成**: メッセージ内容に基づいて3つの返信候補を自動生成
- **ワンクリック返信**: 選択した候補で即座にプラットフォームに返信
- **リアルタイムメッセージ取得**: Booking.com/Airbnb APIから新しいメッセージを自動取得
- **学習機能**: 過去の対応ログから学習し、返信品質を向上

### 対応ユースケース
- 「この場所に荷物おいていいですか？」
- 「予約どれぐらい開いていますか？」
- 「この周辺におすすめの観光地はございますか？」

## システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit    │    │   FastAPI       │    │   PostgreSQL    │
│   Web UI        │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Redis Cache    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │ (Booking.com,   │
                       │  Airbnb, etc.)  │
                       └─────────────────┘
```

## 🚀 クイックスタート（推奨）

### 1. 環境変数の設定

まず、`.env`ファイルを作成してAPIキーを設定します：

```bash
# .envファイルを作成
cp .env.example .env
```

`.env`ファイルを編集して、以下のAPIキーを設定してください：

```bash
# 必須のAPIキー
OPENAI_API_KEY=sk-your-openai-api-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# オプションのAPIキー（モックデータで動作します）
BOOKING_API_KEY=your-booking-api-key-here
AIRBNB_API_KEY=your-airbnb-api-key-here
```

**APIキーの取得方法：**
- **OpenAI API**: https://platform.openai.com/api-keys
- **Google Maps API**: https://console.cloud.google.com/google/maps-apis

### 2. ワンクリックデプロイ

```bash
# デプロイスクリプトを実行
./deploy.sh
```

このスクリプトが以下を自動実行します：
- Dockerコンテナのビルド
- データベースの初期化
- サンプルデータの投入
- 全サービスの起動
- ヘルスチェック

### 3. アクセス

デプロイ完了後、以下のURLにアクセス：

- **🌐 Web UI**: http://localhost:8501
- **📚 API Docs**: http://localhost:8000/docs
- **❤️ ヘルスチェック**: http://localhost:8000/health

## 🔧 手動セットアップ（開発者向け）

### 1. 依存関係のインストール

```bash
# Python仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. データベースのセットアップ

```bash
# PostgreSQLを起動（Dockerを使用）
docker run -d --name postgres-hotel \
  -e POSTGRES_DB=hotel_agent_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15

# Redisを起動（Dockerを使用）
docker run -d --name redis-hotel \
  -p 6379:6379 \
  redis:7-alpine

# データベーステーブルを作成
python -c "from app.database import create_tables; create_tables()"

# サンプルデータを投入
python app/seed_data.py
```

### 3. アプリケーションの起動

**ターミナル1: FastAPIサーバー**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**ターミナル2: Streamlit UI**
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

## 📱 使用方法

### 1. 初回セットアップ

1. **Web UIにアクセス**: http://localhost:8501
2. **ホテルを登録**: サイドバーで「ホテル選択」→ 新しいホテルを登録
3. **サンプルデータ確認**: 既に3つのサンプルホテルが登録済み

### 2. メッセージ管理の流れ

1. **メッセージ取得**
   - 「メッセージ管理」タブを開く
   - 「新しいメッセージを取得」ボタンをクリック
   - サンプルメッセージが自動生成される

2. **返信候補の生成**
   - 未処理メッセージの「返信候補を取得」をクリック
   - 3つの返信候補が自動生成される

3. **返信の送信**
   - 適切な候補を選択
   - 「この候補で返信」をクリック
   - プラットフォームに自動送信

### 3. 分析データの確認

- 「分析」タブで予約パターンや学習結果を確認
- 「ホテル情報」タブで周辺観光地情報を取得

## 🛠️ トラブルシューティング

### よくある問題と解決方法

**1. ポートが使用中エラー**
```bash
# ポート使用状況を確認
lsof -i :8000
lsof -i :8501

# プロセスを終了
kill -9 <PID>
```

**2. Dockerコンテナが起動しない**
```bash
# ログを確認
docker-compose logs

# コンテナを再ビルド
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**3. データベース接続エラー**
```bash
# PostgreSQLの状態を確認
docker ps | grep postgres

# データベースを再作成
docker-compose down -v
docker-compose up -d postgres
```

**4. APIキーエラー**
```bash
# .envファイルの内容を確認
cat .env

# APIキーの有効性をテスト
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### ログの確認方法

```bash
# 全サービスのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f api
docker-compose logs -f streamlit
docker-compose logs -f postgres
```

### システム動作確認

```bash
# 自動テストスクリプトを実行
python test_system.py

# または手動でヘルスチェック
curl http://localhost:8000/health
curl http://localhost:8501
```

## 🔄 開発・カスタマイズ

### 新しいメッセージタイプの追加

1. `app/services/api_service.py`の`categorize_message`メソッドを更新
2. `app/services/response_generator.py`に新しい生成ロジックを追加
3. データベースにテンプレートを追加

### 新しいプラットフォームの統合

1. `app/services/api_service.py`に新しいAPIサービスクラスを追加
2. `MessageProcessor`に統合ロジックを追加
3. `.env`ファイルにAPIキーを追加

### データベースのリセット

```bash
# 全データを削除して再作成
docker-compose down -v
docker-compose up -d postgres redis
sleep 10
python -c "from app.database import create_tables; create_tables()"
python app/seed_data.py
```


## API エンドポイント

### ホテル管理
- `GET /hotels` - ホテル一覧取得
- `POST /hotels` - 新しいホテル作成

### メッセージ管理
- `GET /messages/{hotel_id}` - メッセージ一覧取得
- `POST /messages/fetch/{hotel_id}` - 新しいメッセージ取得
- `POST /messages/{message_id}/suggestions` - 返信候補生成
- `POST /messages/{message_id}/respond` - 返信送信

### 分析・情報
- `GET /hotels/{hotel_id}/analytics` - 分析データ取得
- `GET /hotels/{hotel_id}/nearby-attractions` - 周辺観光地取得

## アーキテクチャ詳細

### エージェントシステム

#### 1. ホテル周辺情報検索エージェント (`HotelInfoAgent`)
- Google Maps APIを使用した周辺施設検索
- 荷物預かり情報の提供
- 予約可能期間の分析
- 観光地情報の取得

#### 2. 予約データ学習エージェント (`BookingDataAgent`)
- 過去のメッセージ・返信ログから学習
- TF-IDFベクトル化による類似メッセージ検索
- 予約パターン分析
- 返信テンプレートの最適化

### データベース設計

- **hotels**: ホテル基本情報
- **bookings**: 予約データ
- **guest_messages**: ゲストメッセージ
- **response_templates**: 返信テンプレート
- **response_logs**: 返信ログ
- **nearby_attractions**: 周辺観光地情報

## 開発・カスタマイズ

### 新しいメッセージタイプの追加

1. `MessageProcessor.categorize_message()`を更新
2. `ResponseGenerator`に新しい生成ロジックを追加
3. データベースにテンプレートを追加

### 新しいプラットフォームの統合

1. `api_service.py`に新しいAPIサービスクラスを追加
2. `MessageProcessor`に統合ロジックを追加
3. 設定ファイルにAPIキーを追加

## トラブルシューティング

### よくある問題

1. **API接続エラー**
   - `.env`ファイルのAPIキーを確認
   - ネットワーク接続を確認

2. **データベース接続エラー**
   - PostgreSQLが起動しているか確認
   - 接続文字列を確認

3. **メッセージ取得エラー**
   - 外部APIの制限を確認
   - APIキーの有効性を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

質問やサポートが必要な場合は、GitHubのIssuesセクションでお知らせください。