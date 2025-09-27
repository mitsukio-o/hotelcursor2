import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

# ページ設定
st.set_page_config(
    page_title="ホテル返信システム",
    page_icon="🏨",
    layout="wide"
)

# APIベースURL
API_BASE_URL = "http://localhost:8000"

# セッション状態の初期化
if 'selected_hotel' not in st.session_state:
    st.session_state.selected_hotel = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []

def fetch_hotels() -> List[Dict]:
    """ホテル一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/hotels")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("ホテル一覧の取得に失敗しました")
            return []
    except Exception as e:
        st.error(f"API接続エラー: {str(e)}")
        return []

def fetch_messages(hotel_id: int) -> List[Dict]:
    """メッセージ一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/messages/{hotel_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("メッセージの取得に失敗しました")
            return []
    except Exception as e:
        st.error(f"API接続エラー: {str(e)}")
        return []

def fetch_response_suggestions(message_id: int, hotel_id: int) -> Dict:
    """返信候補を取得"""
    try:
        response = requests.post(f"{API_BASE_URL}/messages/{message_id}/suggestions", 
                               params={"hotel_id": hotel_id})
        if response.status_code == 200:
            return response.json()
        else:
            st.error("返信候補の取得に失敗しました")
            return {}
    except Exception as e:
        st.error(f"API接続エラー: {str(e)}")
        return {}

def send_response(message_id: int, response_content: str, platform: str) -> Dict:
    """返信を送信"""
    try:
        response = requests.post(f"{API_BASE_URL}/messages/{message_id}/respond",
                               params={
                                   "response_content": response_content,
                                   "platform": platform
                               })
        if response.status_code == 200:
            return response.json()
        else:
            st.error("返信の送信に失敗しました")
            return {}
    except Exception as e:
        st.error(f"API接続エラー: {str(e)}")
        return {}

def main():
    st.title("🏨 ホテル返信システム")
    st.markdown("---")
    
    # サイドバー
    with st.sidebar:
        st.header("ホテル選択")
        
        # ホテル一覧を取得
        hotels = fetch_hotels()
        
        if hotels:
            hotel_options = {f"{hotel['name']} ({hotel['city']})": hotel for hotel in hotels}
            selected_hotel_name = st.selectbox(
                "ホテルを選択してください",
                options=list(hotel_options.keys()),
                index=0 if not st.session_state.selected_hotel else None
            )
            
            if selected_hotel_name:
                st.session_state.selected_hotel = hotel_options[selected_hotel_name]
                
                # ホテル情報を表示
                hotel = st.session_state.selected_hotel
                st.subheader("ホテル情報")
                st.write(f"**名前:** {hotel['name']}")
                st.write(f"**住所:** {hotel['address']}")
                st.write(f"**都市:** {hotel['city']}")
                st.write(f"**国:** {hotel['country']}")
                
                # 新しいメッセージを取得
                if st.button("新しいメッセージを取得", type="primary"):
                    with st.spinner("メッセージを取得中..."):
                        result = requests.post(f"{API_BASE_URL}/messages/fetch/{hotel['id']}")
                        if result.status_code == 200:
                            st.success("メッセージを取得しました")
                            st.rerun()
                        else:
                            st.error("メッセージの取得に失敗しました")
        else:
            st.warning("ホテルが見つかりません。まずホテルを登録してください。")
    
    # メインコンテンツ
    if st.session_state.selected_hotel:
        hotel = st.session_state.selected_hotel
        
        # タブを作成
        tab1, tab2, tab3 = st.tabs(["📨 メッセージ管理", "📊 分析", "🏨 ホテル情報"])
        
        with tab1:
            st.header("メッセージ管理")
            
            # メッセージ一覧を取得
            messages = fetch_messages(hotel['id'])
            
            if messages:
                st.subheader(f"未処理メッセージ ({len([m for m in messages if not m['is_processed']])}件)")
                
                for message in messages:
                    if not message['is_processed']:
                        with st.expander(f"📩 {message['platform']} - {message['message_content'][:50]}..."):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**メッセージ:** {message['message_content']}")
                                st.write(f"**プラットフォーム:** {message['platform']}")
                                st.write(f"**受信時刻:** {message['timestamp']}")
                                st.write(f"**メッセージタイプ:** {message['message_type']}")
                            
                            with col2:
                                if st.button(f"返信候補を取得", key=f"suggest_{message['id']}"):
                                    with st.spinner("返信候補を生成中..."):
                                        suggestions_data = fetch_response_suggestions(message['id'], hotel['id'])
                                        st.session_state.suggestions = suggestions_data.get('suggestions', [])
                                        st.session_state.current_message = message
                                
                                # 返信候補を表示
                                if st.session_state.suggestions and st.session_state.current_message['id'] == message['id']:
                                    st.subheader("返信候補")
                                    
                                    for i, suggestion in enumerate(st.session_state.suggestions):
                                        st.write(f"**候補 {i+1}:**")
                                        st.write(suggestion['content'])
                                        st.write(f"*信頼度: {suggestion['confidence']:.2f} | タイプ: {suggestion['type']}*")
                                        
                                        if st.button(f"この候補で返信", key=f"send_{message['id']}_{i}"):
                                            with st.spinner("返信を送信中..."):
                                                result = send_response(
                                                    message['id'],
                                                    suggestion['content'],
                                                    message['platform']
                                                )
                                                
                                                if result.get('result', {}).get('success'):
                                                    st.success("返信を送信しました！")
                                                    st.rerun()
                                                else:
                                                    st.error("返信の送信に失敗しました")
                                        
                                        st.markdown("---")
            else:
                st.info("新しいメッセージはありません")
        
        with tab2:
            st.header("分析データ")
            
            if st.button("分析データを更新"):
                with st.spinner("分析データを取得中..."):
                    response = requests.get(f"{API_BASE_URL}/hotels/{hotel['id']}/analytics")
                    if response.status_code == 200:
                        analytics = response.json()
                        
                        st.subheader("予約分析")
                        booking_analysis = analytics.get('booking_analysis', {})
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("総予約数", booking_analysis.get('total_bookings', 0))
                        with col2:
                            st.metric("平均滞在日数", f"{booking_analysis.get('average_stay_duration', 0):.1f}日")
                        with col3:
                            st.metric("平均宿泊人数", f"{booking_analysis.get('average_guest_count', 0):.1f}人")
                        
                        st.subheader("人気の部屋タイプ")
                        room_types = booking_analysis.get('popular_room_types', {})
                        if room_types:
                            for room_type, count in room_types.items():
                                st.write(f"**{room_type}:** {count}件")
                        
                        st.subheader("学習結果")
                        learning_result = analytics.get('learning_result', {})
                        st.write(f"処理済みメッセージ: {learning_result.get('messages_processed', 0)}件")
                        st.write(f"処理済み返信: {learning_result.get('responses_processed', 0)}件")
                        st.write(f"読み込み済みテンプレート: {learning_result.get('templates_loaded', 0)}件")
                    else:
                        st.error("分析データの取得に失敗しました")
        
        with tab3:
            st.header("ホテル情報")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("周辺観光地")
                if st.button("観光地情報を取得"):
                    with st.spinner("観光地情報を取得中..."):
                        response = requests.get(f"{API_BASE_URL}/hotels/{hotel['id']}/nearby-attractions")
                        if response.status_code == 200:
                            attractions_data = response.json()
                            attractions = attractions_data.get('attractions', [])
                            
                            for attraction in attractions:
                                st.write(f"**{attraction['name']}**")
                                st.write(f"カテゴリ: {attraction['category']}")
                                st.write(f"距離: {attraction['distance_km']}km")
                                st.write(f"評価: {attraction['rating']}/5")
                                st.write(f"住所: {attraction['address']}")
                                st.markdown("---")
                        else:
                            st.error("観光地情報の取得に失敗しました")
            
            with col2:
                st.subheader("ホテル詳細")
                st.write(f"**ホテル名:** {hotel['name']}")
                st.write(f"**住所:** {hotel['address']}")
                st.write(f"**都市:** {hotel['city']}")
                st.write(f"**国:** {hotel['country']}")
    
    else:
        st.info("サイドバーからホテルを選択してください")

if __name__ == "__main__":
    main()