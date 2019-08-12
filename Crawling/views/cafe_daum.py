# Daum Cafe 처리

from django.http import JsonResponse
from bs4 import BeautifulSoup

from Crawling.views.crawling import init_crawling, DAUM_CAFE_ID


# ===== Config =====
DAUM_CAFE_URL = 'http://m.cafe.daum.net'  # 공통 다음 카페 URL (모바일용)
SEL_DRIVER = init_crawling(headless_mode=True, target='daum', need_login=True)  # Driver를 가져온다.
# ==================


def get_board_list(request):
    """
    게시판 리스트와 정보를 가져오는 함수
    :return: Dict 반환
    """
    result_data = {}  # 응답 데이터를 담을 객체
    SEL_DRIVER.get(DAUM_CAFE_URL + DAUM_CAFE_ID + '/')  # 게시판 메인으로 접근한다.
    html = SEL_DRIVER.page_source  # 페이지 소스를 가져온다.
    soup = BeautifulSoup(html, 'html.parser')

    # 카페 제목
    result_data['title'] = soup.find('strong', class_='tit_visual').text

    # 게시판 숫자
    result_data['board_cnt'] = soup.find('div', class_='#all_board').find('span', class_='num_cafe').text

    board_url = []  # url과 게시판 이름을 저장하는 곳
    for data in soup.find_all('a', {'class': 'link_cafe'}):
        board_url.append({'name': data.find('span', {'class', 'txt_detail'}).text,
                          'url': (data.get('href').split('?')[0])})
    result_data['board_url'] = board_url  # 게시판 정보와 URL Code를 담은 배열을 반환

    return JsonResponse(result_data, content_type='application/json; charset=utf-8',
                        json_dumps_params={'ensure_ascii': False})


def get_board_content_list(request):
    """
    특정 게시판의 게시글 리스트를 가져오는 함수
    :return:
    """
    page = 1  # 기본으로 조회할 페이지 숫자
    result_data = {}  # 응답 데이터를 담을 객체

    # 헤더 값을 조회
    url_code = request.META.get('HTTP_URL_CODE')  # 헤더이 있는 값을 가져오는 부분
    send_page = request.META.get('HTTP_PAGE')  # 페이지
    if url_code is None:  # URL CODE가 같이 전달되지 않은 경우
        return JsonResponse({'fail': 'Wrong url code. (Need header in [url-code]'},
                            content_type='application/json; charset=utf-8',
                            json_dumps_params={'ensure_ascii': False})

    # 페이지 설정
    if send_page is not None and send_page.isdecimal() is True:
        page = send_page

    url = DAUM_CAFE_URL + url_code + '?prev_page=1&firstbbsdepth=0006G&lastbbsdepth=0005w&' + '&page=' + str(page)
    SEL_DRIVER.get(url)  # 게시판 메인으로 접근한다.

    html = SEL_DRIVER.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 총 페이지 갯수를 가져오는 로직
    for data in soup.findAll('script'):
        if 'var pageConfig = {' in data.text:
            for word in data.text.split('\n'):
                if 'totalPage' in word:
                    result_data['totalPage'] = word.strip().split(':')[1].replace(',', '').replace(' ', '')

    # 페이지 정보를 담는 부분
    board_info = []
    for data in soup.find('div', {'id': 'slideArticleList'}).find_all('li'):
        if data.find('span', {'class': 'txt_state'}) is None:
            board_info.append({'title': data.find('span', {'class': 'txt_detail'}).text,
                               'url': data.find('a', {'class': 'link_cafe'})['href']})

    result_data['data'] = board_info
    return JsonResponse(result_data, content_type='application/json; charset=utf-8',
                        json_dumps_params={'ensure_ascii': False})


def get_board_content(request):
    """
    특정 게시판의 글을 가져오는 메서드
    :param request:
    :return:
    """
    result_data = {}  # 응답 데이터를 담을 객체

    # 헤더 값을 조회
    url_code = request.META.get('HTTP_URL_CODE')  # 헤더이 있는 값을 가져오는 부분

    # 헤더에 URL Code가 같이 응답되지 않은 경우
    if url_code is None:
        return JsonResponse({'fail': 'Wrong url code. (Need header in [url-code]'},
                            content_type='application/json; charset=utf-8',
                            json_dumps_params={'ensure_ascii': False})

    url = DAUM_CAFE_URL + url_code
    SEL_DRIVER.get(url)  # 전달된 게시글을 읽는다.

    html = SEL_DRIVER.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 본문
    content_body = soup.find('div', {'id': 'article'})
    make_content = ''  # 만들어진 본문을 저장할 변수
    print('content_body = ', content_body)
    for tag in content_body.find_all(['p', 'br', 'img']):  # 세 가지 태그만 가져온다.
        if tag.name == 'p':
            if 'style' in tag.attrs.keys():
                if '' != tag.text:
                    make_content += '<p>' + tag.text + '</p>'
        else:
            make_content += str(tag)
    result_data['content_body'] = make_content

    # 작성자 정보
    writer_info = soup.find('span', {'class': 'txt_subject'})
    result_data['write_user'] = writer_info.text.split('|')[0][3:]
    result_data['write_date'] = writer_info.find('span', {'class': 'num_subject'}).text

    return JsonResponse(result_data)
