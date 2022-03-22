from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox as msgbox
import os
import pandas as pd
import time
from bs4 import BeautifulSoup
import requests
import webbrowser
import sys

root = Tk()
root.title("디시인사이드 게시물 필터 0.0.1 Beta")


# pyinstaller를 위한 path 코드 (내장 파일)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon = resource_path("icon.ico")
root.iconbitmap(default = icon)

# 갤러리 입력 프레임 (갤러리 명 입력 Entry)
gall_frame = Frame(root)
gall_frame.pack(fill='x', padx=5, pady=5)

label_gall = Label(gall_frame, text='갤러리 주소')
label_gall.pack(side='left', padx=5, pady=5)

entry_gall = Entry(gall_frame, justify='left')
entry_gall.pack(side='left', fill='x',padx=5, pady=5, ipady=4, expand=True)


# 테이블 프레임
table_frame = Frame(root)
table_frame.pack(fill='both', padx=5, pady=5)

scrollbar_y = Scrollbar(table_frame)
scrollbar_y.pack(side="right", fill='y')
scrollbar_x = Scrollbar(table_frame, orient='horizontal')
scrollbar_x.pack(side='bottom', fill='x')
columns = ['번호', '말머리', '제목', '댓글수', '닉네임', 'ID/IP', '작성시간', '조회수', '추천수', '']
width_columns = [65, 60, 345, 45, 95, 95, 150, 45, 45, 0]
table_result = ttk.Treeview(table_frame, columns=columns, height=10, displaycolumns=['번호', '말머리', '제목', '댓글수', '조회수', '추천수', '닉네임', 'ID/IP', '작성시간', ''],
                            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
table_result.pack(side='left', fill='both', expand='True')

table_result.column("#0", width=0, stretch=NO)
table_result.heading("#0", text="")

for column, width in zip(columns, width_columns):
    anchor = CENTER
    if column == '제목':
        anchor = W
    table_result.column(column, anchor=anchor, width=40)
    table_result.heading(column, text=column, anchor=CENTER)
table_result.update()
for column, width in zip(columns, width_columns):
    if column == '':
        table_result.column("", width=0, stretch=NO)
    else:
        table_result.column(column, width=width)

# table_result.column("", width=0, stretch=NO)
# table_result.heading("", text="")

scrollbar_y.config(command=table_result.yview)
scrollbar_x.config(command=table_result.xview)

## 테이블 링크 열기
def link_table(event):
    input_id = table_result.selection()
    url = table_result.item(input_id, "value")[-1]
    # print(table_result.item(input_id))
    webbrowser.open(url)

table_result.bind("<Double-1>", link_table)

# 저장 경로 (폴더)
def browse_dest_path():
    try:
        folder_selected = filedialog.askdirectory(initialdir=txt_dest_path.get())
    except:
        folder_selected = filedialog.askdirectory(initialdir=os.path.abspath("."))
    if folder_selected == '': # 취소를 누를 때
        return
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, folder_selected)


# 필터
def filter_content(soup, i, n_recomm, n_reply, n_cnt, criteria_recomm, criteria_reply, criteria_cnt):
    try:
        gall_subject = soup.select('td.gall_subject')[i].text
    except:
        gall_subject = soup.select('td.gall_num')[i].text
    if gall_subject in ['공지', '설문', 'AD']:
        return False

    title = soup.select('td.gall_tit')[i].text.split('\n')
    gall_rep = title[-1]
    try:
        gall_rep = int(gall_rep[1:-2])
    except:
        gall_rep = 0

    gall_count = int(soup.select('td.gall_count')[i].text)
    gall_recommend = int(soup.select('td.gall_recommend')[i].text)

    def return_condition(criteria, gall, n):
        if criteria == '이상':
            return gall >= n
        else:
            return gall <= n
    
    condition_recomm = return_condition(criteria_recomm, gall_recommend, n_recomm)
    condition_reply = return_condition(criteria_reply, gall_rep, n_reply)
    condition_cnt = return_condition(criteria_cnt, gall_count, n_cnt)

    if condition_recomm and condition_reply and condition_cnt:
        return True
    
    return False


# 검색 결과
def get_info(soup, i, url):
    # 게시물 번호
    gall_num = int(soup.select('td.gall_num')[i].text)
    
    # 게시물 말머리
    try:
        gall_subject = soup.select('td.gall_subject')[i].text
    except:
        gall_subject = ''
    
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
    # 마이너 갤러리
    if 'mgallery' in url:
        gall_url = f'https://gall.dcinside.com/mgallery/board/view/?id={gall_id}&no={gall_num}'
    # 미니 갤러리
    elif 'mini' in url:
        gall_url = f'https://gall.dcinside.com/mini/board/view?id={gall_id}&no={gall_num}'
    # 정식 갤러리
    else:
        gall_url = f'https://gall.dcinside.com/board/view?id={gall_id}&no={gall_num}'
    
    return [gall_num, gall_subject, gall_tit, gall_rep, gall_writer, gall_uid, gall_date, gall_count, gall_recommend, gall_url]

logline = 0
iid = 0
def main():
    global logline, iid
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    url = entry_gall.get()
    
    page1 = int(entry_page1.get())
    page2 = int(entry_page2.get())

    page_start = min(page1, page2)
    page_end = max(page1, page2)

    n_recomm = int(entry_recomm.get())
    n_reply = int(entry_reply.get())
    n_cnt = int(entry_cnt.get())

    criteria_recomm = cmb_recomm.get()
    criteria_reply = cmb_reply.get()
    criteria_cnt = cmb_cnt.get()

    response = requests.get(url, headers=headers).content
    soup = BeautifulSoup(response, 'lxml')
    gall_name = soup.select('div.page_head')[0].find('a').text
    if 'mgallery' in url:
        gall_name = gall_name[:-3]
    elif 'mini' in url:
        gall_name = gall_name[:-2]
        

    list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> {gall_name}에서 게시글을 검색 중입니다.')
    list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> 필터 조건: 추천수 {n_recomm} 이상, 댓글 {n_reply}개 이상, 조회수 {n_cnt} 이상, 페이지 {page_start}-{page_end}')
    
    infos = []
    for page in range(page_start, page_end+1):
        list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> {page}페이지 검색 중...')
        response = requests.get(url, headers=headers, params={'page':page}).content
        soup = BeautifulSoup(response, 'lxml')
        time.sleep(0.1)
        root.update()
        for i in range(len(soup.select('td.gall_num'))):
            if filter_content(soup, i, n_cnt=n_cnt, n_recomm=n_recomm, n_reply=n_reply,
                              criteria_recomm=criteria_recomm, criteria_reply=criteria_reply, criteria_cnt=criteria_cnt):
                info = get_info(soup, i, url)
                if info in infos:
                    continue
                infos.append(info)

                # 테이블 업데이트
                table_result.insert(parent='', index='end', iid=iid, values=[i for i in info])
                iid += 1
                root.update()

        list_log.delete(logline)
        list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> {page}페이지 검색 완료')
        p_var.set((page-page_start+1)/(page_end-page_start+1)*100)
        progress_bar.update()

    list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> 게시글 검색이 끝났습니다.')
    list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> 검색된 게시글: {len(infos)}건')

    df = pd.DataFrame(infos, columns=['번호', '말머리', '제목', '댓글수', '닉네임', 'ID/IP', '작성시간', '조회수', '추천수', 'URL'])
    df = df.drop_duplicates()

    gall_num_min, gall_num_max = df['번호'].min(), df['번호'].max()
    command_save = save_variable.get()
    if command_save:
        output_folder = txt_dest_path.get()
        output_format = cmb_format.get()
        output_name = f'{gall_name}_{gall_num_min}_{gall_num_max}{output_format}'
        if output_format == '.xlsx':
            df.to_excel(os.path.join(output_folder, output_name), index=None)
        else:
            df.to_csv(os.path.join(output_folder, output_name), index=None, encoding='utf-8-sig')

        msgbox.showinfo('완료', '저장이 완료되었습니다.')
    else:
        msgbox.showinfo('완료', '검색이 완료되었습니다.')

# 시작
def start():

    # 페이지 범위 확인
    page1 = entry_page1.get()
    page2 = entry_page2.get()
    
    if not page1 or not page2:
        msgbox.showwarning("경고", "올바른 페이지 범위를 입력하세요. (1 이상)")
        return

    page_start = int(min(page1, page2))
    if page_start == 0:
        msgbox.showwarning("경고", "올바른 페이지 범위를 입력하세요. (1 이상)")
        return

    # 저장 경로 확인
    dest = txt_dest_path.get()
    command_save = save_variable.get()
    if command_save and not dest:
        msgbox.showwarning("경고", "저장 폴더를 지정하지 않았습니다.")
        return

    # DC 주소 확인
    url = entry_gall.get()
    if 'gall.dcinside.com' not in url:
        msgbox.showwarning("경고", "올바른 갤러리 주소가 아닙니다.")
        return

    # 테이블 초기화
    for item in table_result.get_children():
        table_result.delete(item)

    state_some = [entry_cnt, entry_gall, entry_page1, entry_page2, entry_recomm, entry_reply, check_save, btn_start]
    state_cmb = [cmb_cnt, cmb_recomm, cmb_reply]
    state_save = [txt_dest_path, btn_dest_path]
    state_save2 = [cmb_format]
    def state_updater(state, state_list):
        for t in state_list:
            t.configure(state=state)

    # main()
    try:
        p_var.set(0)
        state_updater('disabled', state_some)
        state_updater('disabled', state_cmb)
        if save_variable.get() == 1:
            state_updater('disabled', state_save)
            state_updater('disabled', state_save2)
        main()
        state_updater('normal', state_some)
        state_updater('readonly', state_cmb)
        if save_variable.get() == 1:
            state_updater('normal', state_save)
            state_updater('readonly', state_save2)
    except Exception as e:
        list_log.insert(logline, f'<{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}> 에러로 인해 중단되었습니다.')
        msgbox.showerror("에러", "필터링 중 에러가 발생하였습니다.\n - 잘못된 갤러리 주소명\n - 추천수/댓글수/조회수 입력값 이상\n - 잘못된 저장 폴더 주소 등")
        state_updater('normal', state_some)
        state_updater('readonly', state_cmb)
        if save_variable.get() == 1:
            state_updater('normal', state_save)
            state_updater('readonly', state_save2)
        # print(e)
        return


# 필터 프레임
frame_filter = LabelFrame(root, text='필터')
frame_filter.pack(padx=5, pady=5, ipady=5, expand=True, fill='x')

# 숫자만 입력 받도록
def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True

## 추천수
label_recomm = Label(frame_filter, text='추천수')
label_recomm.pack(side='left', padx=3, pady=5)

entry_recomm = Entry(frame_filter, width=5, justify='center', validate="key")
entry_recomm.pack(side='left', fill='x',padx=1, pady=5, ipady=4)
entry_recomm.insert(0, 0)

entry_recomm['validatecommand'] = (entry_recomm.register(testVal),'%P','%d')

opt_recomm = ['이상', '이하']
cmb_recomm = ttk.Combobox(frame_filter, state='readonly', values=opt_recomm, width=4)
cmb_recomm.current(0)
cmb_recomm.pack(side='left', padx=1, pady=5)

## 댓글수
label_reply = Label(frame_filter, text='   댓글수')
label_reply.pack(side='left', padx=3, pady=5)

entry_reply = Entry(frame_filter, width=5, justify='center', validate="key")
entry_reply.pack(side='left', fill='x', padx=1, pady=5, ipady=4)
entry_reply.insert(0, 0)

entry_reply['validatecommand'] = (entry_reply.register(testVal),'%P','%d')

opt_reply = ['이상', '이하']
cmb_reply = ttk.Combobox(frame_filter, state='readonly', values=opt_reply, width=4)
cmb_reply.current(0)
cmb_reply.pack(side='left', padx=1, pady=5)

## 조회수
label_cnt = Label(frame_filter, text='   조회수')
label_cnt.pack(side='left', padx=3, pady=5)

entry_cnt = Entry(frame_filter, width=5, justify='center', validate="key")
entry_cnt.pack(side='left', fill='x', padx=1, pady=5, ipady=4)
entry_cnt.insert(0, 0)

entry_cnt['validatecommand'] = (entry_cnt.register(testVal),'%P','%d')

opt_cnt = ['이상', '이하']
cmb_cnt = ttk.Combobox(frame_filter, state='readonly', values=opt_cnt, width=4)
cmb_cnt.current(0)
cmb_cnt.pack(side='left', padx=1, pady=5)

## 페이지
label_page = Label(frame_filter, text='   페이지')
label_page.pack(side='left', padx=3, pady=5)

entry_page1 = Entry(frame_filter, width=5, justify='center', validate="key")
entry_page1.pack(side='left', fill='x', padx=3, pady=5, ipady=4)

label_page_dash = Label(frame_filter, text='-')
label_page_dash.pack(side='left')

entry_page2 = Entry(frame_filter, width=5, justify='center', validate="key")
entry_page2.pack(side='left', fill='x', padx=3, pady=5, ipady=4)

entry_page1['validatecommand'] = (entry_page1.register(testVal),'%P','%d')
entry_page2['validatecommand'] = (entry_page2.register(testVal),'%P','%d')

## 저장 함수
def save_select():
    if save_variable.get() == 0:
        txt_dest_path.configure(state='disabled')
        btn_dest_path.configure(state='disabled')
        cmb_format.configure(state='disabled')
    else:
        txt_dest_path.configure(state='normal')
        btn_dest_path.configure(state='normal')
        cmb_format.configure(state='readonly')

## 저장
save_variable = IntVar()
check_save = Checkbutton(frame_filter, text='파일 저장', variable=save_variable, command=save_select)
check_save.pack(side='left', padx=10, pady=5, fill='x')
save_variable.set(0)


# 저장 경로 프레임
path_frame = LabelFrame(root, text='저장경로')
path_frame.pack(fill='x', padx=5, pady=5, ipady=5)

txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side='left', fill='x', expand=True, padx=5, pady=5, ipady=4)
txt_dest_path.insert(0, os.path.abspath("."))

btn_dest_path = Button(path_frame, text='찾아보기', width=10, command = browse_dest_path)
btn_dest_path.pack(side='left', padx=5, pady=5)

## 파일 포맷 옵션
## 파일 포맷 옵션 레이블
lbl_format = Label(path_frame, text='포맷', width=8)
lbl_format.pack(side='left', padx=5, pady=5)

## 파일 포맷 옵션 콤보
opt_format = ['.xlsx', '.csv']
cmb_format = ttk.Combobox(path_frame, state='readonly', values=opt_format, width=10)
cmb_format.current(0)
cmb_format.pack(side='left', padx=5, pady=5)



# 진행 상황 progress bar
frame_progress = LabelFrame(root, text='진행 상황')
frame_progress.pack(fill='x', padx=5, pady=5, ipady=5)

p_var = DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill='x', padx=5, pady=5)

# 실행 프레임
frame_run = Frame(root)
frame_run.pack(fill='x', padx=5, pady=5)

def close_program():
    root.destroy()
    root.quit()

btn_close = Button(frame_run, padx=5, pady=5, text='닫기', width=12, command=close_program)
btn_close.pack(side='right', padx=5, pady=5)

btn_start = Button(frame_run, padx=5, pady=5, text='실행', width=12, command=start)
btn_start.pack(side='right', padx=5, pady=5)


log_open = True
def log_open_close():
    global log_open
    if log_open:
        btn_log.configure(text='로그 열기')
        log_frame.pack_forget()
        log_open = False
        root.geometry("731x578")
    else:
        btn_log.configure(text='로그 닫기')
        log_frame.pack(fill='both', padx=5, pady=5)
        log_open = True
        root.geometry("731x672")

btn_log = Button(frame_run, padx=5, pady=5, text='로그 닫기', width=12, command=log_open_close)
btn_log.pack(side='left', padx=5, pady=5)


# 로그 프레임
log_frame = Frame(root)
log_frame.pack(fill='both', padx=5, pady=5)

log_scrollbar = Scrollbar(log_frame)
log_scrollbar.pack(side="right", fill='y')

list_log = Listbox(log_frame, selectmode="extended", height=5, width=100,
                    yscrollcommand=log_scrollbar.set)
list_log.pack(side='left', fill='both', expand=True)
log_scrollbar.config(command=list_log.yview)


root.resizable(False, False)
root.geometry("731x672")
save_select()

root.mainloop()