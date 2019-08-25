"""
Utils
"""

from Crawling import utils


def is_blank(target_str):
    """
    전달된 문자열이 공백인지 아닌지 체크하는 함수
    :param target_str:
    :return:
    """
    if target_str and target_str.strip():
        # myString is not None AND myString is not empty or blank
        return False
    # myString is None OR myString is empty or blank
    return True


def get_content_by_tag_filter(content_html, filter_tag):
    """

    :param content_html:
    :param filter_tag:
    :return:
    """
    make_content = ''  # 만들어진 본문을 저장할 변수
    for tag in content_html.find_all(filter_tag):  # 세 가지 태그만 가져온다.
        if tag.name == 'p':  # tag by <p>
            if str(tag) != '<p> </p>' and not utils.is_blank(tag.text):  # 공백 태그가 온 경우에는 넘긴다.
                make_content += '<p>' + tag.text.strip() + '</p>'
        elif tag.name == 'img':
            make_content += '<img src=' + tag['src'] + '/>'
        else:  # P를 제외한 나머지 태그
            make_content += str(tag)
    return make_content
