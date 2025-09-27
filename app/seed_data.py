from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Hotel, Booking, ResponseTemplate
from datetime import datetime, timedelta
import random

def create_sample_hotels(db: Session):
    """サンプルホテルデータを作成"""
    hotels = [
        Hotel(
            name="東京グランドホテル",
            address="東京都千代田区丸の内1-1-1",
            latitude=35.6762,
            longitude=139.6503,
            city="東京",
            country="日本"
        ),
        Hotel(
            name="大阪ビジネスホテル",
            address="大阪府大阪市北区梅田1-1-1",
            latitude=34.6937,
            longitude=135.5023,
            city="大阪",
            country="日本"
        ),
        Hotel(
            name="京都伝統旅館",
            address="京都府京都市下京区四条通烏丸西入ル",
            latitude=35.0116,
            longitude=135.7681,
            city="京都",
            country="日本"
        )
    ]
    
    for hotel in hotels:
        db.add(hotel)
    
    db.commit()
    return hotels

def create_sample_bookings(db: Session, hotels):
    """サンプル予約データを作成"""
    bookings = []
    
    for hotel in hotels:
        # 各ホテルに5-10件の予約を作成
        num_bookings = random.randint(5, 10)
        
        for i in range(num_bookings):
            check_in = datetime.now() + timedelta(days=random.randint(-30, 30))
            check_out = check_in + timedelta(days=random.randint(1, 7))
            
            booking = Booking(
                hotel_id=hotel.id,
                guest_name=f"ゲスト{i+1}",
                check_in=check_in,
                check_out=check_out,
                room_type=random.choice(["シングル", "ダブル", "ツイン", "スイート"]),
                guest_count=random.randint(1, 4),
                booking_reference=f"REF{hotel.id:03d}{i+1:03d}",
                status=random.choice(["confirmed", "cancelled", "completed"])
            )
            
            bookings.append(booking)
            db.add(booking)
    
    db.commit()
    return bookings

def create_sample_templates(db: Session, hotels):
    """サンプル返信テンプレートを作成"""
    templates = []
    
    # 荷物預かり関連のテンプレート
    luggage_templates = [
        "お荷物の預かりサービスをご利用いただけます。フロントデスクまでお越しください。",
        "チェックイン前・チェックアウト後もお荷物をお預かりいたします。",
        "お荷物は安全に保管いたしますのでご安心ください。"
    ]
    
    # 予約関連のテンプレート
    availability_templates = [
        "空室状況をお調べいたします。ご希望の日程をお教えください。",
        "ご予約可能な期間をご案内いたします。お急ぎの場合はお電話にてお問い合わせください。",
        "お早めのご予約をお勧めいたします。"
    ]
    
    # 観光地関連のテンプレート
    attraction_templates = [
        "周辺の観光地をご案内いたします。おすすめスポットをご紹介いたします。",
        "ホテル周辺の観光情報をお調べいたします。アクセス方法もご案内いたします。",
        "地元の隠れた名所もご紹介いたします。お気軽にお尋ねください。"
    ]
    
    for hotel in hotels:
        # 荷物預かりテンプレート
        for template in luggage_templates:
            response_template = ResponseTemplate(
                hotel_id=hotel.id,
                message_type="luggage",
                template_content=template,
                language="ja",
                is_active=True
            )
            templates.append(response_template)
            db.add(response_template)
        
        # 予約関連テンプレート
        for template in availability_templates:
            response_template = ResponseTemplate(
                hotel_id=hotel.id,
                message_type="availability",
                template_content=template,
                language="ja",
                is_active=True
            )
            templates.append(response_template)
            db.add(response_template)
        
        # 観光地テンプレート
        for template in attraction_templates:
            response_template = ResponseTemplate(
                hotel_id=hotel.id,
                message_type="attractions",
                template_content=template,
                language="ja",
                is_active=True
            )
            templates.append(response_template)
            db.add(response_template)
    
    db.commit()
    return templates

def seed_database():
    """データベースにサンプルデータを投入"""
    db = SessionLocal()
    
    try:
        print("サンプルデータの作成を開始...")
        
        # ホテルデータを作成
        hotels = create_sample_hotels(db)
        print(f"{len(hotels)}件のホテルを作成しました")
        
        # 予約データを作成
        bookings = create_sample_bookings(db, hotels)
        print(f"{len(bookings)}件の予約を作成しました")
        
        # テンプレートデータを作成
        templates = create_sample_templates(db, hotels)
        print(f"{len(templates)}件のテンプレートを作成しました")
        
        print("サンプルデータの作成が完了しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()