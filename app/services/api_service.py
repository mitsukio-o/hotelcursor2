import aiohttp
import asyncio
from typing import List, Dict, Optional
from app.config import settings
import json
from datetime import datetime

class BookingAPIService:
    def __init__(self):
        self.api_key = settings.BOOKING_API_KEY
        self.base_url = settings.BOOKING_API_URL
    
    async def get_guest_messages(self, hotel_id: str) -> List[Dict]:
        """Booking.comからゲストメッセージを取得"""
        # 実際の実装ではBooking.comのAPIを使用
        # ここではモックデータを返す
        
        mock_messages = [
            {
                'id': 'msg_001',
                'booking_id': 'book_001',
                'guest_name': '田中太郎',
                'message': 'この場所に荷物おいていいですか？',
                'timestamp': datetime.now().isoformat(),
                'platform': 'booking.com'
            },
            {
                'id': 'msg_002',
                'booking_id': 'book_002',
                'guest_name': '佐藤花子',
                'message': '予約どれぐらい開いていますか？',
                'timestamp': datetime.now().isoformat(),
                'platform': 'booking.com'
            },
            {
                'id': 'msg_003',
                'booking_id': 'book_003',
                'guest_name': '山田次郎',
                'message': 'この周辺におすすめの観光地はございますか？',
                'timestamp': datetime.now().isoformat(),
                'platform': 'booking.com'
            }
        ]
        
        return mock_messages
    
    async def send_response(self, message_id: str, response_content: str) -> Dict:
        """Booking.comに返信を送信"""
        # 実際の実装ではBooking.comのAPIを使用
        # ここではモックレスポンスを返す
        
        return {
            'success': True,
            'message_id': message_id,
            'response_id': f'resp_{message_id}',
            'sent_at': datetime.now().isoformat(),
            'platform': 'booking.com'
        }

class AirbnbAPIService:
    def __init__(self):
        self.api_key = settings.AIRBNB_API_KEY
        self.base_url = settings.AIRBNB_API_URL
    
    async def get_guest_messages(self, listing_id: str) -> List[Dict]:
        """Airbnbからゲストメッセージを取得"""
        # 実際の実装ではAirbnbのAPIを使用
        # ここではモックデータを返す
        
        mock_messages = [
            {
                'id': 'airbnb_msg_001',
                'listing_id': listing_id,
                'guest_name': 'John Smith',
                'message': 'Can I store my luggage here?',
                'timestamp': datetime.now().isoformat(),
                'platform': 'airbnb'
            },
            {
                'id': 'airbnb_msg_002',
                'listing_id': listing_id,
                'guest_name': 'Maria Garcia',
                'message': 'What are the availability dates?',
                'timestamp': datetime.now().isoformat(),
                'platform': 'airbnb'
            }
        ]
        
        return mock_messages
    
    async def send_response(self, message_id: str, response_content: str) -> Dict:
        """Airbnbに返信を送信"""
        # 実際の実装ではAirbnbのAPIを使用
        # ここではモックレスポンスを返す
        
        return {
            'success': True,
            'message_id': message_id,
            'response_id': f'airbnb_resp_{message_id}',
            'sent_at': datetime.now().isoformat(),
            'platform': 'airbnb'
        }

class MessageProcessor:
    def __init__(self):
        self.booking_service = BookingAPIService()
        self.airbnb_service = AirbnbAPIService()
    
    async def fetch_all_messages(self, hotel_id: str, listing_id: str = None) -> List[Dict]:
        """全プラットフォームからメッセージを取得"""
        tasks = []
        
        # Booking.comからメッセージを取得
        tasks.append(self.booking_service.get_guest_messages(hotel_id))
        
        # Airbnbからメッセージを取得（listing_idが提供されている場合）
        if listing_id:
            tasks.append(self.airbnb_service.get_guest_messages(listing_id))
        
        # 並列でメッセージを取得
        results = await asyncio.gather(*tasks)
        
        # 結果を統合
        all_messages = []
        for result in results:
            all_messages.extend(result)
        
        return all_messages
    
    async def send_response_to_platform(self, platform: str, message_id: str, response_content: str) -> Dict:
        """指定されたプラットフォームに返信を送信"""
        if platform == 'booking.com':
            return await self.booking_service.send_response(message_id, response_content)
        elif platform == 'airbnb':
            return await self.airbnb_service.send_response(message_id, response_content)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def categorize_message(self, message: str) -> str:
        """メッセージをカテゴリに分類"""
        message_lower = message.lower()
        
        # 荷物関連
        luggage_keywords = ['荷物', 'バッグ', 'スーツケース', '預かり', 'luggage', 'bag', 'suitcase']
        if any(keyword in message_lower for keyword in luggage_keywords):
            return 'luggage'
        
        # 予約関連
        booking_keywords = ['予約', '空室', '空き', 'availability', 'booking', 'reservation']
        if any(keyword in message_lower for keyword in booking_keywords):
            return 'availability'
        
        # 観光地関連
        attraction_keywords = ['観光', '観光地', 'おすすめ', '観光スポット', 'attraction', 'sightseeing', 'recommend']
        if any(keyword in message_lower for keyword in attraction_keywords):
            return 'attractions'
        
        return 'general'