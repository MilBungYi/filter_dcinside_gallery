import pandas as pd
from tqdm import trange
import time
from bs4 import BeautifulSoup
import requests

def filter_content(soup, i, n_recomm, n_reply, n_cnt):
    gall_subject = soup.select('td.gall_subject')[i].text
    if gall_subject == '공지':
        return False
    title = soup.select('td.gall_tit')[i].text.split('\n')
    gall_rep = title[-1]
    try:
        gall_rep = int(gall_rep[1:-2])
    except:
        gall_rep = 0
    gall_count = int(soup.select('td.gall_count')[i].text)
    gall_recommend = int(soup.select('td.gall_recommend')[i].text)
    if gall_rep >= n_reply and gall_count >= n_cnt and gall_recommend >= n_recomm:
        return True
    
    return False

def get_info(soup, i, url):
    # 게시물 번호
    gall_num = int(soup.select('td.gall_num')[i].text)
    
    # 게시물 말머리
    gall_subject = soup.select('td.gall_subject')[i].text
    
    # 게시물 제목, 댓글수
    title = soup.select('td.gall_tit')[i].text.split('\n')
    gall_tit, gall_rep = title[1], title[-1]
    try:
        gall_rep = int(gall_rep[1:-2])
    except:
        gall_rep = 0
    
    # 게시물 작성자 닉네임, ID(IP)
    gall_writer = soup.select('td.gall_writer')[i]
    gall_uid = gall_writer.get('data-uid')
    if not gall_uid:
        gall_uid = gall_writer.get('data-ip')
    gall_writer = gall_writer.get('data-nick')
    
    # 게시물 작성 시간
    gall_date = soup.select('td.gall_date')[i]
    gall_date = gall_date.get('title')
    
    # 게시물 조회수
    gall_count = int(soup.select('td.gall_count')[i].text)
    
    # 게시물 추천수
    gall_recommend = int(soup.select('td.gall_recommend')[i].text)
    
    # url
    gall_id = url.split('?id=')[-1]
    gall_url = f'https://gall.dcinside.com/mgallery/board/view/?id={gall_id}&no={gall_num}'
    
    return [gall_num, gall_subject, gall_tit, gall_rep, gall_writer, gall_uid, gall_date, gall_count, gall_recommend, gall_url]

def main():
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    url = input('> 갤러리 주소를 입력하세요: ')
    while True:
        try:
            page1, page2 = map(int, input('> 검색 페이지 범위를 입력하세요: ').split())
        except:
            print('> 잘못된 입력입니다.')
            continue
        
        page_start = min(page1, page2)
        page_end = max(page1, page2)
        
        if page_start <= 0:
            print('> 잘못된 입력입니다. 1 이상의 두 숫자를 입력하세요.')
            continue
        break

    while True:
        try:
            n_recomm, n_reply, n_cnt = map(int, input('> 필터 조건을 입력하세요(추천수 댓글수 조회수): ').split())
        except:
            print('> 잘못된 입력입니다.')
            continue
            
        if n_recomm < 0 or n_reply < 0 or n_cnt < 0:
            print('> 잘못된 입력입니다. 0 이상의 세 숫자를 입력하세요.')
            continue
        break

    infos = []
    print('> 게시글을 검색 중입니다.')
    print(f'> 필터 조건: 추천수 {n_recomm} 이상, 댓글 {n_reply}개 이상, 조회수 {n_cnt} 이상')
    time.sleep(0.5)
    for page in trange(page_start, page_end+1):
        response = requests.get(url, headers=headers, params={'page':page}).content
        soup = BeautifulSoup(response, 'lxml')
        time.sleep(0.1)
        for i in range(len(soup.select('td.gall_num'))):
            if filter_content(soup, i, n_cnt=n_cnt, n_recomm=n_recomm, n_reply=n_reply):
                info = get_info(soup, i, url)
                infos.append(info)
        time.sleep(0.1)
    
    time.sleep(0.5)
    print('> 게시글 검색이 끝났습니다.')
    print(f'> 검색된 게시글: {len(infos)}건')
    df = pd.DataFrame(infos, columns=['번호', '말머리', '제목', '댓글수', '닉네임', 'ID/IP', '작성시간', '조회수', '추천수', 'URL'])
    df = df.drop_duplicates()

    gall_name = soup.select('div.page_head')[0].find('a').text
    if gall_name.endswith('마이너'):
        gall_name = gall_name[:-3]
    gall_num_min, gall_num_max = df['번호'].min(), df['번호'].max()
    command_save = input('> 검색 결과를 파일로 저장하시겠습니까? (Y/N): ')
    if command_save.lower() == 'y':
        output_name = f'{gall_name}_{gall_num_min}_{gall_num_max}.xlsx'
        df.to_excel(output_name, index=None)
        print(f'검색 결과를 저장하였습니다. [{output_name}]')
    print(df[['번호', '제목', '댓글수', '조회수', '추천수', '닉네임', 'ID/IP']])

if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            print('잘못된 입력으로 인해 오류가 발생하였습니다. (갤러리 주소를 잘못 입력 등의 이유)')
        command = input('> 프로그램을 종료하시겠습니까? (Y/N) :')
        if command.lower() == 'y':
            break
