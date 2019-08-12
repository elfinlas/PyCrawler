# Crawling 공통 모듈

import time
from selenium import webdriver
from PyCrawling.settings import BASE_DIR

# ===== Config =====
# DAUM INFO
DAUM_ID = 'test'
DAUM_PW = 'test'
DAUM_CAFE_ID = 'test'
# ==================


def init_crawling(headless_mode, target, need_login):
    """
    크롤링을 위한 기본 도구를 초기화 해주는 함수
    :param headless_mode: Headless 동작 여부
    :param target: 크롤링 대상
    :param need_login: 로그인 필요 여부
    :return:
    """
    print('Init with webdriver.')
    options = webdriver.ChromeOptions()

    if headless_mode:
        options.add_argument('headless')

    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    # Headless 탐지를 막기 위해 사람 흉내
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36")
    options.add_argument("lang=ko_KR")  # 한국어!

    # Driver를 가져온다.
    driver = webdriver.Chrome(BASE_DIR + '/chromedriver', chrome_options=options)

    if need_login is True:
        if target.lower() == 'daum':
            login_daum(driver)

    return driver


def login_daum(driver):
    # 로그인 URL 호출
    driver.implicitly_wait(3)  # 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
    driver.get(
        'https://logins.daum.net/accounts/signinform.do?url=http%3A%2F%2Fm.cafe.daum.net%2F_myCafe%3Fnull')

    #  로그인 작업
    driver.find_element_by_xpath("""//*[@id="id"]""").send_keys(DAUM_ID)  # id
    driver.find_element_by_xpath("""//*[@id="inputPwd"]""").send_keys(DAUM_PW)  # 패스워드
    time.sleep(0.6)  # 0.6초 뒤 수행
    driver.find_element_by_xpath("""//*[@id="loginBtn"]""").click()  # 입력 버튼 클릭.
    time.sleep(0.3)  # 0.3초 뒤 수행 (게시판 이동 등)
