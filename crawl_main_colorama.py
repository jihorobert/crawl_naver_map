from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from selenium import webdriver
import pandas as pd
import os
import sys
from colorama import init, Fore, Style

init()

# 실행 파일 위치 가져오기
def get_exe_dir():
    if getattr(sys, 'frozen', False):
        # 실행 파일이 있는 디렉토리
        return os.path.dirname(sys.executable)
    else:
        # 스크립트가 실행되는 디렉토리
        return os.path.dirname(os.path.abspath(__file__))

# 크롤링 데이터 저장
data = []

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.102 Safari/537.36')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)
# 대기 시간
driver.implicitly_wait(time_to_wait=10)
# 반복 종료 조건
loop = True
keyword = input("검색어 입력: ")
URL = f'https://map.naver.com/p/search/{keyword}'
driver.get(url=URL)

def switch_left():
    ############## iframe으로 왼쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)

def switch_right():
    ############## iframe으로 오른쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)


# 시작
while(True):
    switch_left()

    # 페이지 숫자를 초기에 체크 [ True / False ]
    # 이건 페이지 넘어갈때마다 계속 확인해줘야 함 (페이지 새로 로드 될때마다 버튼 상태 값이 바뀜)
    # next_page = driver.find_element(By.XPATH, '//*[@class="XUrfU"]//div[2]/a[7]').get_attribute('aria-disabled')
    all_links = driver.find_elements(By.XPATH, '//*[@class="XUrfU"]//div[2]/a')
    last_link = all_links[-1]
    next_page = last_link.get_attribute('aria-disabled')
    # print('next_page: ', next_page)

    ############## 맨 밑까지 스크롤 ##############
    # 스크롤 할 요소 찾기
    scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)

    while True:
        # 현재 스크롤 위치를 계산
        current_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_element)
        max_scroll = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)

        # 스크롤을 맨 아래까지 이동
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_element)
        sleep(2)  # 동적 로드를 기다림

        # 스크롤이 더 이상 증가하지 않으면 종료
        new_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_element)
        if new_scroll == current_scroll:
            break


    ############## 현재 page number 가져오기 - 1 페이지 ##############
    page_no = driver.find_element(By.XPATH,'//a[contains(@class, "mBN2s qxokY")]').text

    # 현재 페이지에 등록된 모든 가게 조회
    # 첫페이지 광고 2개 때문에 첫페이지는 앞 2개를 빼야함
    if(page_no == '1'):
        elements = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')[2:]
    else:
        elements = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')

    print('\n현재 ' + Fore.GREEN + str(page_no) + Fore.RESET + ' 페이지 / '+ '총 ' + Fore.GREEN + str(len(elements)) + Fore.RESET + '개의 가게를 찾았습니다.')

    print(Fore.YELLOW + "-"*50 + Fore.RESET)

    switch_left()

    sleep(2)

    # 모든 리스트를 각 하나씩 클릭하면서 상세 페이지에서 원하는값(=주소,연락처) 가져오면 끝
    for index, e in enumerate(elements, start=1):
        store_name = '' # 가게 이름
        address = '' # 가게 주소
        phone_num = '' # 연락처

        switch_left()

        # 순서대로 값을 하나씩 클릭
        # 식당 검색시에는 위에 평점, 리뷰, 카테고리 등이 있어서 다른 div태그를 선택해야함
        try:
            name_element = e.find_element(By.CLASS_NAME, 'ouxiq').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
        except NoSuchElementException:
            name_element = e.find_element(By.CLASS_NAME, 'CHC5F').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
        # name_element = e.find_element(By.CLASS_NAME,'ouxiq').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
        name_element_name = name_element.text
        driver.execute_script("arguments[0].click();", name_element)
        sleep(2)
        switch_right()

        ################### 크롤링 시작 ##################
        # 업체 진입
        # flag -> 정보 가져오기 성공시 0, 실패시 1
        flag = 0
        for i in range(10):
            try:
                sleep(1)
                title = driver.find_element(By.XPATH, '//div[@class="zD5Nm undefined"]')
                flag = 0
                break
            except NoSuchElementException:
                flag = 1
                print(Fore.RED + f"Element not found on this page. Retrying...({i+1}/10)" + Fore.RESET)
                sleep(2)
                switch_left()
                name_element = e.find_element(By.CLASS_NAME,'ouxiq').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
                driver.execute_script("arguments[0].click();", name_element)
                sleep(2)
                switch_right()
        if flag == 1:
            print(Fore.RED + f"Element not found on this page. Skipping this one." + Fore.RESET)
            continue

        # 가게 이름
        try:
            store_name = title.find_element(By.XPATH,'.//div[1]/div[1]/span[1]').text
        except:
            print(Fore.RED + '------------ 가게 이름 부분 오류 or 존재 하지 않음 ------------' + Fore.RESET)
            store_name = 'N/A'
        # 가게 주소
        try:
            address = driver.find_element(By.XPATH,'//span[@class="LDgIH"]').text
        except:
            print(Fore.RED + '------------ 가게 주소 부분 오류 or 존재 하지 않음 ------------' + Fore.RESET)
            address = 'N/A'
        # 가게 연락처
        try:
            phone_num = driver.find_element(By.XPATH,'//span[@class="xlx7Q"]').text
        except:
            print(Fore.RED + '------------ 가게 연락처 부분 오류 or 존재 하지 않음 ------------' + Fore.RESET)
            phone_num = 'N/A'
        
        data.append({
            'store_name': store_name,
            'address': address,
            'phone_num': phone_num
        })

        print(str(index) + ". " + name_element_name)
        print('가게 주소 ' + Fore.GREEN + str(address) + Fore.RESET)
        print('가게 번호 ' + Fore.GREEN + phone_num + Fore.RESET)
        print(Fore.MAGENTA + "-"*50 + Fore.RESET)

    switch_left()

    # 페이지 다음 버튼이 활성화 상태일 경우 계속 진행
    if(next_page == 'false'):
        last_link.click()
    # 아닐 경우 루프 정지
    else:
        loop = False
        break

# 엑셀 파일 저장
output_dir = get_exe_dir()  # 실행 파일 위치
output_path = os.path.join(output_dir, f"{keyword}_crawling_result.xlsx")
df = pd.DataFrame(data)
df.index += 1
df.to_excel(output_path, engine='openpyxl')
print(f"엑셀 파일 저장 완료: {output_path}")

driver.quit()