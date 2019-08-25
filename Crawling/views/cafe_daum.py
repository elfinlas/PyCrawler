# Daum Cafe 처리

from django.http import JsonResponse
from bs4 import BeautifulSoup

from Crawling.views.crawling import init_crawling, DAUM_CAFE_ID
from Crawling import utils


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
    SEL_DRIVER.get(DAUM_CAFE_URL + DAUM_CAFE_ID)  # 게시판 메인으로 접근한다.
    html = SEL_DRIVER.page_source  # 페이지 소스를 가져온다.
    soup = BeautifulSoup(html, 'html.parser')

    # 카페 제목
    result_data['title'] = soup.find('strong', class_='tit_visual').text

    # 게시판 숫자
    result_data['board_cnt'] = soup.find('div', class_='#all_board').find('span', class_='num_cafe').text

    board_url = []  # url과 게시판 이름을 저장하는 곳
    for data in soup.find_all('a', {'class': 'link_cafe'}):
        board_url.append({'name': data.find('span', {'class', 'txt_detail'}).text,
                          'url': (DAUM_CAFE_URL+data.get('href').split('?')[0])})
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

    url = url_code + '?prev_page=1&firstbbsdepth=0006G&lastbbsdepth=0005w&' + '&page=' + str(page)
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
            board_info.append({'name': data.find('span', {'class': 'txt_detail'}).text,
                               'url': DAUM_CAFE_URL[:-1]+data.find('a', {'class': 'link_cafe'})['href']})

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

    # url = DAUM_CAFE_URL + url_code
    url = url_code
    SEL_DRIVER.get(url)  # 전달된 게시글을 읽는다.

    html = SEL_DRIVER.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 본문
    make_content = utils.get_content_by_tag_filter(soup.find('div', {'id': 'article'}), ['p', 'br', 'img'])
    result_data['content_body'] = make_content  # 최종적으로 게시글 컨텐츠 저장

    # 첨부파일이 존재하는 경우
    if soup.find('div', {'class', 'file_add'}) is not None:
        attach_file_list = []  # 첨부파일 데이터를 담을 배열
        for tag_a in soup.find('ul', {'class', 'list_file'}):
            if type(tag_a.find('a')) is not int:
                attach_file_list.append(
                    dict(name=tag_a.find('span', {'class', 'file_name'}).text,
                         url=tag_a.find('a')['href'])
                )
        # 첨부파일 갯수
        attach_file_info = dict(
            attach_cnt=soup.find('div', {'class', 'file_add'}).find('strong', {'class', 'txt_num'}).text,
            attach_file=attach_file_list)
        result_data['attach_file'] = attach_file_info
    else:  # 첨부파일이 없는 경우 빈 데이터 추가
        result_data['attach_file'] = dict(attach_cnt=0, attach_file=[])

    # 작성자 정보
    writer_info = soup.find('span', {'class': 'txt_subject'})
    result_data['write_user'] = writer_info.text.split('|')[0][3:]
    result_data['write_date'] = writer_info.find('span', {'class': 'num_subject'}).text

    return JsonResponse(result_data)