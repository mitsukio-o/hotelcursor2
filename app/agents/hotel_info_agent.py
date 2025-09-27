import googlemaps
import requests
from typing import List, Dict, Optional
from app.config import settings
from app.models import Hotel, NearbyAttraction
from sqlalchemy.orm import Session
import json

class HotelInfoAgent:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    
    def get_nearby_attractions(self, hotel_id: int, db: Session, radius: int = 2000) -> List[Dict]:
        """ホテル周辺の観光地・施設を取得"""
        # ホテル情報を取得
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            return []
        
        # Google Places APIで周辺施設を検索
        places_result = self.gmaps.places_nearby(
            location=(hotel.latitude, hotel.longitude),
            radius=radius,
            type=['tourist_attraction', 'restaurant', 'shopping_mall', 'park']
        )
        
        attractions = []
        for place in places_result.get('results', []):
            attraction_data = {
                'name': place.get('name'),
                'category': self._categorize_place(place.get('types', [])),
                'rating': place.get('rating', 0),
                'address': place.get('vicinity'),
                'latitude': place.get('geometry', {}).get('location', {}).get('lat'),
                'longitude': place.get('geometry', {}).get('location', {}).get('lng'),
                'distance_km': self._calculate_distance(
                    hotel.latitude, hotel.longitude,
                    place.get('geometry', {}).get('location', {}).get('lat'),
                    place.get('geometry', {}).get('location', {}).get('lng')
                )
            }
            attractions.append(attraction_data)
        
        return attractions
    
    def get_luggage_storage_info(self, hotel_id: int, db: Session) -> Dict:
        """荷物預かり情報を取得"""
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            return {}
        
        # ホテル周辺のコインロッカーや荷物預かりサービスを検索
        places_result = self.gmaps.places_nearby(
            location=(hotel.latitude, hotel.longitude),
            radius=1000,
            keyword='コインロッカー 荷物預かり'
        )
        
        storage_options = []
        for place in places_result.get('results', []):
            storage_options.append({
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'rating': place.get('rating', 0),
                'distance_km': self._calculate_distance(
                    hotel.latitude, hotel.longitude,
                    place.get('geometry', {}).get('location', {}).get('lat'),
                    place.get('geometry', {}).get('location', {}).get('lng')
                )
            })
        
        return {
            'hotel_name': hotel.name,
            'hotel_address': hotel.address,
            'storage_options': storage_options,
            'hotel_storage_available': True  # 仮の値、実際はホテルデータから取得
        }
    
    def get_booking_availability(self, hotel_id: int, db: Session) -> Dict:
        """予約可能期間を取得"""
        hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            return {}
        
        # 実際の実装では、ホテルの予約システムAPIと連携
        # ここでは仮のデータを返す
        return {
            'hotel_name': hotel.name,
            'availability': {
                'next_30_days': 'limited',
                'next_90_days': 'available',
                'peak_season': '2024-07-15 to 2024-08-31',
                'off_season': '2024-09-01 to 2024-12-31'
            },
            'recommended_booking_window': '30-60 days in advance'
        }
    
    def _categorize_place(self, types: List[str]) -> str:
        """Google Placesのタイプを日本語カテゴリに変換"""
        type_mapping = {
            'tourist_attraction': '観光地',
            'restaurant': 'レストラン',
            'shopping_mall': 'ショッピング',
            'park': '公園',
            'museum': '博物館',
            'amusement_park': 'テーマパーク',
            'zoo': '動物園',
            'aquarium': '水族館'
        }
        
        for place_type in types:
            if place_type in type_mapping:
                return type_mapping[place_type]
        return 'その他'
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """2点間の距離を計算（km）"""
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth's radius in kilometers
        return round(c * r, 2)