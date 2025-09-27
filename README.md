# ホテル向け自動返信システムについて

Booking.comやAirbnbなどのプラットフォームからのゲストメッセージに対して、AIを活用した自動返信候補を生成し、ワンクリックで返信できるシステムです。

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

## セットアップ

### 1. 環境変数の設定

`.env`ファイルを作成し、必要なAPIキーを設定してください：

```bash
cp .env.example .env
```

以下のAPIキーを設定：
- `OPENAI_API_KEY`: OpenAI APIキー
- `GOOGLE_MAPS_API_KEY`: Google Maps APIキー
- `BOOKING_API_KEY`: Booking.com APIキー（オプション）
- `AIRBNB_API_KEY`: Airbnb APIキー（オプション）

### 2. Docker Composeを使用した起動

```bash
# アプリケーションを起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# アプリケーションを停止
docker-compose down
```

### 3. 手動セットアップ

```bash
# 依存関係をインストール
pip install -r requirements.txt

# データベースを初期化
python -c "from app.database import create_tables; create_tables()"

# サンプルデータを投入
python app/seed_data.py

# FastAPIサーバーを起動
python -m uvicorn app.main:app --reload

# 別のターミナルでStreamlitを起動
streamlit run streamlit_app.py
```

## 使用方法

### 1. Webインターフェースにアクセス

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs

### 2. ホテル登録

1. Streamlit UIで「ホテル選択」セクションを使用
2. 新しいホテルを登録（API経由）

### 3. メッセージ管理

1. 「メッセージ管理」タブで新しいメッセージを取得
2. 未処理メッセージの「返信候補を取得」をクリック
3. 生成された3つの候補から選択
4. 「この候補で返信」をクリックして送信

### 4. 分析データの確認

「分析」タブで以下の情報を確認：
- 予約パターン分析
- 学習結果
- メッセージ処理統計

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