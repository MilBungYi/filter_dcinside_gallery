# 디시인사이드 갤러리 게시물 필터링 앱
디시공앱의 필터링 기능을 PC에서도 사용하기 위한 앱 개발 프로젝트

## 필요한 패키지
- `python=3.8.8`
- `pandas=1.2.4`
- `tqdm=4.59.0`
- `beautifulsoup4=4.9.3`
- `requests=2.25.1`

## 구현 목록
- [x] 입력 받은 갤러리의 페이지 내에서 필터링
- [x] 추천수, 댓글수, 조회수에 따라 필터링
- [ ] tkinter를 이용한 GUI 개발

## 실행 예시
1. filter_app.py
실행하면 값을 입력받아 필터 기능 실행
- 갤러리 주소
- 검색할 페이지 범위: 1 이상의 두 숫자 입력
  - 1 10
- 추천수, 댓글수, 조회수: 0 이상의 세 숫자 입력
  - 3 5 10
- 파일 저장: Y/N 입력
![app_py](https://user-images.githubusercontent.com/102043866/159292809-5f0af79a-5dee-473e-860b-881149938f3d.png)


2. filter_app_arg.py
```
usage: filter_app_arg.py [-h] --gallery GALLERY [--reply REPLY] [--cnt CNT]
                         [--recommend RECOMMEND] [--pages PAGES] [--save SAVE]

Filter Contents in DCInside Gallery

optional arguments:
  -h, --help            show this help message and exit
  --gallery GALLERY, -g GALLERY
                        URL of gallery
  --reply REPLY, -r REPLY
                        a condition for the number of comments to filter posts
                        (default: 0)
  --cnt CNT, -c CNT     a condition for the number of views to filter posts
                        (default: 0)
  --recommend RECOMMEND, -m RECOMMEND
                        a condition for the number of recommends to filter
                        posts (default: 0)
  --pages PAGES, -p PAGES
                        pages to search posts (a-b)
  --save SAVE, -s SAVE  save result to excel file (default:Y) (Y/N)
```
실행할 때 값을 입력받아 필터 기능 실행
- 갤러리 주소: -g 갤러리 주소
  - -g https://...
- 검색할 페이지 범위: -p 범위1-범위2
  - -p 1-10
- 추천수: -m 숫자
  - -m 3
- 댓글수: -r 숫자
  - -r 5
- 조회수: -c 숫자
  - -c 10
- 파일 저장: -s Y/N
![app_arg_py](https://user-images.githubusercontent.com/102043866/159292860-cd44ef37-4e93-4113-bfc3-4fe904490ca4.png)
