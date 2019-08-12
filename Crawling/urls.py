from django.urls import path
from .views.cafe_daum import get_board_list, get_board_content_list, get_board_content

urlpatterns = [
    # Daum 게시판 리스트
    path('cafe/daum/board/list', get_board_list, name='get_daum_board_list'),

    # Daum 게시판 컨텐츠 리스트
    path('cafe/daum/board/content/list', get_board_content_list, name='get_daum_board_content_list'),

    # Daum 게시판 컨텐츠
    path('cafe/daum/board/content', get_board_content, name='get_daum_board_content'),
]
