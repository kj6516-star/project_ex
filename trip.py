import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. 저장 설정
output_dir = "naver_trip"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)


def scroll_to_bottom():
    """스크롤을 끝까지 내리며 모든 데이터를 로드함"""
    print("스크롤 중...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 바닥까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 데이터 로딩 대기 시간 충분히 부여

        new_height = driver.execute_script("return document.body.scrollHeight")
        # 더 이상 늘어날 높이가 없으면 종료
        if new_height == last_height:
            # 혹시 모르니 한 번 더 확인 (지연 로딩 대비)
            time.sleep(2)
            if driver.execute_script("return document.body.scrollHeight") == new_height:
                break
        last_height = new_height


# --- 수집 설정 ---
target_big = "강원"
target_small = "춘천"
target_url = "https://travel.naver.com/domestic/01210/autoCourse"
periods = ["당일치기", "1박 2일", "2박 3일", "3박 4일 이상"]
# ----------------

# 모든 데이터를 담을 리스트
all_courses = []

try:
    driver.get(target_url)
    time.sleep(5)

    for pd_name in periods:
        print(f"🔄 필터 적용 및 수집 중: {pd_name}")

        try:
            # 1. 필터 버튼 찾기 및 클릭 (클래스 부분 일치 + 텍스트 매칭)
            filter_xpath = f"//div[contains(@class, 'list_filters')]//button[contains(., '{pd_name}')]"
            target_btn = wait.until(EC.element_to_be_clickable((By.XPATH, filter_xpath)))

            driver.execute_script("arguments[0].scrollIntoView(true);", target_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", target_btn)

            # 필터 클릭 후 리스트가 완전히 바뀔 때까지 대기
            time.sleep(5)

            # 2. 무한 스크롤 실행 (모든 항목 로드)
            scroll_to_bottom()

            # 3. 데이터 수집
            cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='list_course_detail_link']")
            count = 0

            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "strong[class*='list_name']").text
                    link = card.get_attribute('href')

                    # 통합 리스트에 추가
                    all_courses.append({
                        "region_big": target_big,
                        "region_small": target_small,
                        "title": title,
                        "link": link,
                        "period": pd_name
                    })
                    count += 1
                except:
                    continue

            print(f"✅ {pd_name} 수집 완료: {count}개 (누적: {len(all_courses)}개)")

        except Exception as e:
            print(f"⚠️ {pd_name} 필터 처리 중 오류 발생 (건너뜀)")

    # 4. 모든 수집 완료 후 하나의 파일로 저장
    combined_file_name = f"{target_big}_{target_small}_통합리스트.json"
    file_path = os.path.join(output_dir, combined_file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=4)

    print(f"\n💾 최종 저장 완료: {file_path}")
    print(f"📊 총 수집된 코스 개수: {len(all_courses)}개")

finally:
    driver.quit()
