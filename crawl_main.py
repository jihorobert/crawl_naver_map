from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)
# 대기 시간
driver.implicitly_wait(time_to_wait=10)
# 반복 종료 조건
loop = True
keyword = input("검색어 입력: ")
URL = f'https://map.naver.com/p/search/{keyword}'
driver.get(url=URL)

class Colors:
    RESET = "\033[0m"       # 텍스트 색상 초기화
    RED = "\033[31m"        # 빨간색
    GREEN = "\033[32m"      # 초록색
    YELLOW = "\033[33m"     # 노란색
    BLUE = "\033[34m"       # 파란색
    MAGENTA = "\033[35m"    # 자주색
    CYAN = "\033[36m"       # 청록색
    WHITE = "\033[37m"      # 흰색

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
    next_page = driver.find_element(By.XPATH, '//*[@class="XUrfU"]//div[2]/a[7]').get_attribute('aria-disabled')

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

    print('\n현재 ' + '\033[95m' + str(page_no) + '\033[0m' + ' 페이지 / '+ '총 ' + '\033[95m' + str(len(elements)) + '\033[0m' + '개의 가게를 찾았습니다.')

    print(Colors.YELLOW + "-"*50 + Colors.RESET)

    switch_left()

    sleep(2)

    # 모든 리스트를 각 하나씩 클릭하면서 상세 페이지에서 원하는값(=주소,연락처) 가져오면 끝
    for index, e in enumerate(elements, start=1):
        store_name = '' # 가게 이름
        address = '' # 가게 주소
        phone_num = '' # 연락처

        switch_left()

        # 순서대로 값을 하나씩 클릭
        name_element = e.find_element(By.CLASS_NAME,'ouxiq').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
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
                print(Colors.RED + f"Element not found on this page. Retrying...({i+1}/5)" + Colors.RESET)
                sleep(2)
                switch_left()
                name_element = e.find_element(By.CLASS_NAME,'ouxiq').find_element(By.XPATH, ".//a[1]/div[1]/div[1]/span[1]")
                driver.execute_script("arguments[0].click();", name_element)
                sleep(2)
                switch_right()
        if flag == 1:
            print(Colors.RED + f"Element not found on this page. Skipping this one." + Colors.RESET)
            continue

        # 가게 이름
        try:
            store_name = title.find_element(By.XPATH,'.//div[1]/div[1]/span[1]').text
        except:
            print(Colors.RED + '------------ 가게 이름 부분 오류 or 존재 하지 않음 ------------' + Colors.RESET)
            store_name = 'N/A'
        # 가게 주소
        try:
            address = driver.find_element(By.XPATH,'//span[@class="LDgIH"]').text
        except:
            print(Colors.RED + '------------ 가게 주소 부분 오류 or 존재 하지 않음 ------------' + Colors.RESET)
            address = 'N/A'
        # 가게 연락처
        try:
            phone_num = driver.find_element(By.XPATH,'//span[@class="xlx7Q"]').text
        except:
            print(Colors.RED + '------------ 가게 연락처 부분 오류 or 존재 하지 않음 ------------' + Colors.RESET)
            phone_num = 'N/A'

        print(str(index) + ". " + name_element_name)
        print('가게 주소 ' + Colors.GREEN + str(address) + Colors.RESET)
        print('가게 번호 ' + Colors.GREEN + phone_num + Colors.RESET)
        print(Colors.MAGENTA + "-"*50 + Colors.RESET)

    switch_left()

    # 페이지 다음 버튼이 활성화 상태일 경우 계속 진행
    if(next_page == 'false'):
        driver.find_element(By.XPATH, '//*[@class="XUrfU"]//div[2]/a[7]').click()
    # 아닐 경우 루프 정지
    else:
        loop = False
        break