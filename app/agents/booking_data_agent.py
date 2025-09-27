import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import Booking, GuestMessage, ResponseTemplate, ResponseLog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime, timedelta
import json

class BookingDataAgent:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        self.message_vectors = None
        self.template_vectors = None
        self.templates = []
    
    def learn_from_historical_data(self, db: Session, hotel_id: int):
        """過去の対応ログから学習"""
        # 過去のメッセージとレスポンスを取得
        messages = db.query(GuestMessage).join(Booking).filter(
            Booking.hotel_id == hotel_id
        ).all()
        
        responses = db.query(ResponseLog).join(GuestMessage).join(Booking).filter(
            Booking.hotel_id == hotel_id
        ).all()
        
        # テンプレートを取得
        templates = db.query(ResponseTemplate).filter(
            ResponseTemplate.hotel_id == hotel_id,
            ResponseTemplate.is_active == True
        ).all()
        
        self.templates = [template.template_content for template in templates]
        
        # TF-IDFベクトル化
        if self.templates:
            self.template_vectors = self.vectorizer.fit_transform(self.templates)
        
        return {
            'messages_processed': len(messages),
            'responses_processed': len(responses),
            'templates_loaded': len(templates)
        }
    
    def analyze_booking_patterns(self, db: Session, hotel_id: int) -> Dict:
        """予約パターンを分析"""
        bookings = db.query(Booking).filter(Booking.hotel_id == hotel_id).all()
        
        if not bookings:
            return {}
        
        # データフレームに変換
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'guest_count': booking.guest_count,
                'room_type': booking.room_type,
                'status': booking.status
            })
        
        df = pd.DataFrame(booking_data)
        
        # 分析
        analysis = {
            'total_bookings': len(bookings),
            'average_stay_duration': self._calculate_average_stay(df),
            'peak_seasons': self._identify_peak_seasons(df),
            'popular_room_types': df['room_type'].value_counts().to_dict(),
            'average_guest_count': df['guest_count'].mean(),
            'booking_trends': self._analyze_booking_trends(df)
        }
        
        return analysis
    
    def generate_response_suggestions(self, message: str, message_type: str, db: Session, hotel_id: int) -> List[Dict]:
        """メッセージに基づいて返信候補を生成"""
        suggestions = []
        
        # 1. テンプレートベースの候補
        template_suggestions = self._get_template_suggestions(message, message_type, db, hotel_id)
        suggestions.extend(template_suggestions)
        
        # 2. AI生成の候補
        ai_suggestions = self._generate_ai_suggestions(message, message_type, db, hotel_id)
        suggestions.extend(ai_suggestions)
        
        # 3. 過去の成功例ベースの候補
        historical_suggestions = self._get_historical_suggestions(message, message_type, db, hotel_id)
        suggestions.extend(historical_suggestions)
        
        # 重複を除去し、上位3つを返す
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        return unique_suggestions[:3]
    
    def _get_template_suggestions(self, message: str, message_type: str, db: Session, hotel_id: int) -> List[Dict]:
        """テンプレートベースの候補を生成"""
        templates = db.query(ResponseTemplate).filter(
            ResponseTemplate.hotel_id == hotel_id,
            ResponseTemplate.message_type == message_type,
            ResponseTemplate.is_active == True
        ).all()
        
        suggestions = []
        for template in templates:
            suggestions.append({
                'content': template.template_content,
                'type': 'template',
                'confidence': 0.8,
                'source': f'Template: {template.id}'
            })
        
        return suggestions
    
    def _generate_ai_suggestions(self, message: str, message_type: str, db: Session, hotel_id: int) -> List[Dict]:
        """AI生成の候補を作成"""
        # 実際の実装ではOpenAI APIを使用
        # ここでは仮の候補を返す
        
        ai_responses = {
            'luggage': [
                "承知いたしました。お荷物の預かりサービスをご利用いただけます。フロントデスクまでお越しください。",
                "お荷物の預かりは可能です。チェックイン前・チェックアウト後も対応いたします。",
                "お荷物をお預かりいたします。安全に保管いたしますのでご安心ください。"
            ],
            'availability': [
                "現在の空室状況をお調べいたします。ご希望の日程をお教えください。",
                "予約可能な期間をご案内いたします。お急ぎの場合はお電話にてお問い合わせください。",
                "空室カレンダーをご確認いたします。ご希望に合うお部屋をご提案いたします。"
            ],
            'attractions': [
                "周辺の観光地をご案内いたします。おすすめスポットをご紹介いたします。",
                "ホテル周辺の観光情報をお調べいたします。アクセス方法もご案内いたします。",
                "地元の隠れた名所もご紹介いたします。お気軽にお尋ねください。"
            ]
        }
        
        suggestions = []
        responses = ai_responses.get(message_type, [])
        
        for i, response in enumerate(responses):
            suggestions.append({
                'content': response,
                'type': 'ai_generated',
                'confidence': 0.7,
                'source': f'AI Generated #{i+1}'
            })
        
        return suggestions
    
    def _get_historical_suggestions(self, message: str, message_type: str, db: Session, hotel_id: int) -> List[Dict]:
        """過去の成功例ベースの候補を生成"""
        # 過去の類似メッセージとそのレスポンスを検索
        similar_messages = db.query(GuestMessage).join(Booking).filter(
            Booking.hotel_id == hotel_id,
            GuestMessage.message_type == message_type
        ).limit(5).all()
        
        suggestions = []
        for msg in similar_messages:
            response = db.query(ResponseLog).filter(
                ResponseLog.guest_message_id == msg.id,
                ResponseLog.is_sent == True
            ).first()
            
            if response:
                suggestions.append({
                    'content': response.response_content,
                    'type': 'historical',
                    'confidence': 0.6,
                    'source': f'Historical: Message #{msg.id}'
                })
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """重複する候補を除去"""
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
    
    def _calculate_average_stay(self, df: pd.DataFrame) -> float:
        """平均滞在日数を計算"""
        if df.empty or 'check_in' not in df.columns or 'check_out' not in df.columns:
            return 0
        
        df['stay_duration'] = (df['check_out'] - df['check_in']).dt.days
        return df['stay_duration'].mean()
    
    def _identify_peak_seasons(self, df: pd.DataFrame) -> Dict:
        """ピークシーズンを特定"""
        if df.empty or 'check_in' not in df.columns:
            return {}
        
        df['month'] = df['check_in'].dt.month
        monthly_counts = df['month'].value_counts()
        
        peak_months = monthly_counts.head(3).index.tolist()
        return {
            'peak_months': peak_months,
            'monthly_distribution': monthly_counts.to_dict()
        }
    
    def _analyze_booking_trends(self, df: pd.DataFrame) -> Dict:
        """予約トレンドを分析"""
        if df.empty or 'check_in' not in df.columns:
            return {}
        
        df['year_month'] = df['check_in'].dt.to_period('M')
        monthly_trends = df.groupby('year_month').size()
        
        return {
            'monthly_trends': monthly_trends.to_dict(),
            'growth_rate': self._calculate_growth_rate(monthly_trends)
        }
    
    def _calculate_growth_rate(self, trends: pd.Series) -> float:
        """成長率を計算"""
        if len(trends) < 2:
            return 0
        
        first_month = trends.iloc[0]
        last_month = trends.iloc[-1]
        
        if first_month == 0:
            return 0
        
        return ((last_month - first_month) / first_month) * 100