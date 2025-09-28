#!/usr/bin/env python3
"""
ホテル返信システムの動作確認スクリプト
"""

import requests
import time
import json

def test_api_health():
    """APIのヘルスチェック"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPIサービスが正常に動作しています")
            return True
        else:
            print(f"❌ FastAPIサービスが異常です (ステータス: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FastAPIサービスに接続できません: {e}")
        return False

def test_streamlit_ui():
    """Streamlit UIのヘルスチェック"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit UIが正常に動作しています")
            return True
        else:
            print(f"❌ Streamlit UIが異常です (ステータス: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Streamlit UIに接続できません: {e}")
        return False

def test_hotels_api():
    """ホテルAPIのテスト"""
    try:
        response = requests.get("http://localhost:8000/hotels", timeout=5)
        if response.status_code == 200:
            hotels = response.json()
            print(f"✅ ホテルAPIが正常に動作しています ({len(hotels)}件のホテル)")
            return True
        else:
            print(f"❌ ホテルAPIが異常です (ステータス: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ホテルAPIに接続できません: {e}")
        return False

def test_message_suggestions():
    """返信候補生成のテスト"""
    try:
        # テストメッセージIDを使用
        response = requests.post(
            "http://localhost:8000/messages/1/suggestions",
            params={"hotel_id": 1},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            print(f"✅ 返信候補生成が正常に動作しています ({len(suggestions)}件の候補)")
            return True
        else:
            print(f"❌ 返信候補生成が異常です (ステータス: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 返信候補生成に接続できません: {e}")
        return False

def main():
    """メイン実行関数"""
    print("🏨 ホテル返信システムの動作確認を開始します...")
    print("=" * 50)
    
    # 各テストを実行
    tests = [
        ("FastAPIサービス", test_api_health),
        ("Streamlit UI", test_streamlit_ui),
        ("ホテルAPI", test_hotels_api),
        ("返信候補生成", test_message_suggestions),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}をテスト中...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 結果: {passed}/{len(tests)} テストが成功しました")
    
    if passed == len(tests):
        print("\n🎉 すべてのテストが成功しました！")
        print("📱 以下のURLにアクセスしてシステムを使用できます:")
        print("   - Web UI: http://localhost:8501")
        print("   - API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  一部のテストが失敗しました。")
        print("🔧 トラブルシューティング:")
        print("   1. docker-compose ps でコンテナの状態を確認")
        print("   2. docker-compose logs でログを確認")
        print("   3. ./deploy.sh でシステムを再起動")

if __name__ == "__main__":
    main()