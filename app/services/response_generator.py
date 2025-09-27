from typing import List, Dict, Optional
from app.agents.hotel_info_agent import HotelInfoAgent
from app.agents.booking_data_agent import BookingDataAgent
from app.services.api_service import MessageProcessor
from sqlalchemy.orm import Session
from app.models import Hotel, GuestMessage, ResponseLog
import json

class ResponseGenerator:
    def __init__(self):
        self.hotel_info_agent = HotelInfoAgent()
        self.booking_data_agent = BookingDataAgent()
        self.message_processor = MessageProcessor()
    
    async def generate_response_suggestions(
        self, 
        message: str, 
        message_type: str, 
        hotel_id: int, 
        db: Session
    ) -> List[Dict]:
        """メッセージに基づいて返信候補を生成"""
        
        # ホテル情報を取得
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            return []
        
        # メッセージタイプに応じて適切な情報を取得
        context_info = await self._get_context_info(message_type, hotel_id, db)
        
        # 返信候補を生成
        suggestions = []
        
        if message_type == 'luggage':
            suggestions = self._generate_luggage_responses(message, context_info, hotel)
        elif message_type == 'availability':
            suggestions = self._generate_availability_responses(message, context_info, hotel)
        elif message_type == 'attractions':
            suggestions = self._generate_attraction_responses(message, context_info, hotel)
        else:
            suggestions = self._generate_general_responses(message, context_info, hotel)
        
        # 過去のデータから学習した候補も追加
        historical_suggestions = self.booking_data_agent.generate_response_suggestions(
            message, message_type, db, hotel_id
        )
        
        # 候補を統合し、重複を除去
        all_suggestions = suggestions + historical_suggestions
        unique_suggestions = self._deduplicate_and_rank(all_suggestions)
        
        return unique_suggestions[:3]
    
    async def _get_context_info(self, message_type: str, hotel_id: int, db: Session) -> Dict:
        """メッセージタイプに応じたコンテキスト情報を取得"""
        context = {}
        
        if message_type == 'luggage':
            context['luggage_info'] = self.hotel_info_agent.get_luggage_storage_info(hotel_id, db)
        elif message_type == 'availability':
            context['availability_info'] = self.hotel_info_agent.get_booking_availability(hotel_id, db)
        elif message_type == 'attractions':
            context['attractions'] = self.hotel_info_agent.get_nearby_attractions(hotel_id, db)
        
        return context
    
    def _generate_luggage_responses(self, message: str, context_info: Dict, hotel) -> List[Dict]:
        """荷物預かりに関する返信候補を生成"""
        luggage_info = context_info.get('luggage_info', {})
        
        suggestions = [
            {
                'content': f"{hotel.name}では、お荷物の預かりサービスをご利用いただけます。フロントデスクまでお越しください。チェックイン前・チェックアウト後も対応いたします。",
                'type': 'informative',
                'confidence': 0.9,
                'source': 'Hotel Service Info'
            },
            {
                'content': "お荷物をお預かりいたします。安全に保管いたしますのでご安心ください。預かり時間は24時間対応しております。",
                'type': 'reassuring',
                'confidence': 0.8,
                'source': 'Standard Response'
            },
            {
                'content': "承知いたしました。お荷物の預かりは可能です。お部屋の準備ができ次第、お荷物をお部屋までお運びいたします。",
                'type': 'service_oriented',
                'confidence': 0.7,
                'source': 'Personalized Service'
            }
        ]
        
        # 周辺のコインロッカー情報がある場合は追加
        if luggage_info.get('storage_options'):
            suggestions.append({
                'content': f"ホテルでの預かりに加えて、最寄りのコインロッカーもご利用いただけます。{luggage_info['storage_options'][0]['name']}が徒歩圏内にございます。",
                'type': 'comprehensive',
                'confidence': 0.6,
                'source': 'Nearby Options'
            })
        
        return suggestions
    
    def _generate_availability_responses(self, message: str, context_info: Dict, hotel) -> List[Dict]:
        """予約可能期間に関する返信候補を生成"""
        availability_info = context_info.get('availability_info', {})
        
        suggestions = [
            {
                'content': f"{hotel.name}の空室状況をお調べいたします。ご希望の日程をお教えください。お急ぎの場合はお電話にてお問い合わせください。",
                'type': 'inquiry',
                'confidence': 0.9,
                'source': 'Standard Response'
            },
            {
                'content': "現在の空室状況をご案内いたします。ご希望の期間をお教えいただければ、最適なお部屋をご提案いたします。",
                'type': 'service_oriented',
                'confidence': 0.8,
                'source': 'Personalized Service'
            },
            {
                'content': "空室カレンダーをご確認いたします。お早めのご予約をお勧めいたします。",
                'type': 'encouraging',
                'confidence': 0.7,
                'source': 'Booking Encouragement'
            }
        ]
        
        # 利用可能な情報がある場合は追加
        if availability_info.get('availability'):
            suggestions.append({
                'content': f"現在、{availability_info['availability'].get('next_90_days', '通常期間')}のご予約を受け付けております。{availability_info.get('recommended_booking_window', '30日前')}のご予約をお勧めいたします。",
                'type': 'detailed',
                'confidence': 0.8,
                'source': 'Availability Data'
            })
        
        return suggestions
    
    def _generate_attraction_responses(self, message: str, context_info: Dict, hotel) -> List[Dict]:
        """観光地に関する返信候補を生成"""
        attractions = context_info.get('attractions', [])
        
        suggestions = [
            {
                'content': f"{hotel.name}周辺の観光地をご案内いたします。おすすめスポットをご紹介いたしますので、お気軽にお尋ねください。",
                'type': 'general',
                'confidence': 0.8,
                'source': 'Standard Response'
            },
            {
                'content': "ホテル周辺の観光情報をお調べいたします。アクセス方法や営業時間もご案内いたします。",
                'type': 'informative',
                'confidence': 0.7,
                'source': 'Information Service'
            },
            {
                'content': "地元の隠れた名所もご紹介いたします。フロントデスクで観光マップをお渡しいたします。",
                'type': 'local_expert',
                'confidence': 0.6,
                'source': 'Local Knowledge'
            }
        ]
        
        # 具体的な観光地がある場合は追加
        if attractions:
            top_attractions = attractions[:3]
            attraction_names = [attr['name'] for attr in top_attractions]
            
            suggestions.append({
                'content': f"おすすめの観光地をご紹介いたします。{', '.join(attraction_names)}などが徒歩圏内にございます。詳細なアクセス方法をお教えいたします。",
                'type': 'specific',
                'confidence': 0.9,
                'source': 'Nearby Attractions'
            })
        
        return suggestions
    
    def _generate_general_responses(self, message: str, context_info: Dict, hotel) -> List[Dict]:
        """一般的な返信候補を生成"""
        return [
            {
                'content': f"{hotel.name}のスタッフがお手伝いいたします。ご質問がございましたら、お気軽にお声かけください。",
                'type': 'welcoming',
                'confidence': 0.7,
                'source': 'General Response'
            },
            {
                'content': "ご質問を承りました。詳細をお調べいたしますので、少々お待ちください。",
                'type': 'acknowledging',
                'confidence': 0.6,
                'source': 'Acknowledgment'
            },
            {
                'content': "お客様のご要望にお応えできるよう、最善を尽くします。フロントデスクまでお越しください。",
                'type': 'service_oriented',
                'confidence': 0.5,
                'source': 'Service Commitment'
            }
        ]
    
    def _deduplicate_and_rank(self, suggestions: List[Dict]) -> List[Dict]:
        """候補の重複を除去し、信頼度でランク付け"""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            content = suggestion['content']
            if content not in seen:
                seen.add(content)
                unique_suggestions.append(suggestion)
        
        # 信頼度でソート
        unique_suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return unique_suggestions
    
    async def send_response(
        self, 
        message_id: str, 
        response_content: str, 
        platform: str, 
        db: Session
    ) -> Dict:
        """返信を送信し、ログを記録"""
        
        # プラットフォームに返信を送信
        send_result = await self.message_processor.send_response_to_platform(
            platform, message_id, response_content
        )
        
        # データベースにログを記録
        response_log = ResponseLog(
            guest_message_id=int(message_id.split('_')[-1]),  # 仮の実装
            response_content=response_content,
            response_type='automated',
            is_sent=send_result.get('success', False)
        )
        
        db.add(response_log)
        db.commit()
        
        return {
            'success': send_result.get('success', False),
            'response_log_id': response_log.id,
            'platform_response': send_result
        }