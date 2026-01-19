"""
네이버 API 테스트 스크립트
Client ID와 Secret이 올바르게 작동하는지 확인합니다.
"""
import os
from dotenv import load_dotenv
from fetchers.naver_api import NaverShoppingAPI

load_dotenv()

# API 키 확인
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

if not client_id or not client_secret:
    print("❌ 오류: .env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET이 설정되지 않았습니다.")
    print("\n.env 파일에 다음 내용을 추가하세요:")
    print("NAVER_CLIENT_ID=your_client_id")
    print("NAVER_CLIENT_SECRET=your_client_secret")
    exit(1)

print(f"✅ 네이버 API 설정 확인 완료")
print(f"Client ID: {client_id[:10]}..." if len(client_id) > 10 else f"Client ID: {client_id}")

# API 테스트
api = NaverShoppingAPI()
results = api.search("고양이 사료", display=3)

print(f"\n📦 검색 결과: {len(results)} 개")

for i, item in enumerate(results, 1):
    info = api.extract_food_info(item)
    print(f"\n[{i}] {info['name']}")
    print(f"    브랜드: {info['brand']}")

    # 가격 표시 (None 체크)
    if info['min_price'] and info['max_price']:
        print(f"    가격: {info['min_price']:,} 원 ~ {info['max_price']:,} 원")
    elif info['min_price']:
        print(f"    가격: {info['min_price']:,} 원")
    else:
        print("    가격: 정보 없음")

    print(f"    상품 ID: {info['naver_product_id']}")

print("\n✅ 네이버 API 테스트 완료!")
