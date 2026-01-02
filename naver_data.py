import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 1. 파일 불러오기 (아까 저장한 773개 링크)
with open("link_list.json", "r", encoding="utf-8") as f:
    links = json.load(f)

# 2. 브라우저 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
full_data = []

try:
    # 테스트로 앞의 3개만 순회
    for item in links[:3]:
        print(f"🔎 수집 중: {item['title']}")
        driver.get(item['link'])
        time.sleep(6)  # 상세 페이지 로딩 대기

        # [핵심] 페이지의 모든 텍스트 일단 긁기
        # 'body' 태그의 텍스트를 가져오면 화면에 보이는 모든 글자가 잡힙니다.
        page_text = driver.find_element(By.TAG_NAME, "body").text


        # [선택] 장소 리스트만 따로 예쁘게 정리하기
        # 상세 페이지 내 장소 클래스명을 'spot_name'으로 가정 (실제 확인 필요)
        try:
            spot_list=[]
            boxes = driver.find_elements(By.CSS_SELECTOR, "[class*='detail_poi_info']")
            for box in boxes:
                spots = box.find_elements(By.CSS_SELECTOR, "[class*='detail_name']")
                spot = [s.text for s in spots if s.text]
                spot_list.extend(spot)
        except:
            spot_list = []

        full_data.append({
            "title": item['title'],
            "url": item['link'],
            "full_content": page_text,
            "spots": spot_list
        })

    # 3. 결과 저장
    with open("course_details_sample.json", "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    print("✅ 샘플 데이터 수집 완료! course_details_sample.json을 확인하세요.")

finally:
    driver.quit()