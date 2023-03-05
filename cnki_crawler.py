import os
import re
import time

from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

#todo:加上csv功能，每次爬取指定页数功能,保存requirements.txt`

# 搜索关键字
KEYWORD = "人工智能"

def WaitForFive():
    time.sleep(5)

def WaitForTen():
    time.sleep(10)

# 判断是否存在下一页
def HasNextPage(web):
    try:
        web.find_element(By.ID,"PageNext")
        return True
    except:
        print("have no next page")
        return False


def SwitchToDetailWindow(web, url):
    try:
        # web.get(url)
        web.execute_script("window.open('');")
        print("open blank window")
        web.switch_to.window(web.window_handles[-1])
        web.get(url)
        print('switch to new window')
        WaitForFive()
    except:
        print("switch to detail window failed")

def SwitchToSearchResultWindow(web, window_handle):
    try:
        web.close()
        WaitForFive()
        web.switch_to.window(window_handle)
        WaitForTen()
    except:
        print("switch to search result window failed")

# 爬取数据
def StartSpider(web):
    global KEYWORD
    # KEYWORD = "人工智能"
    KEYWORD = input('请输入索引关键字：')

    file_path = './Data/'+KEYWORD
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    WaitForFive()
    try:
        #主页搜索
        web.find_element(By.ID,"txt_SearchText").send_keys(KEYWORD,Keys.ENTER)
        
    except:
        #非主页搜索
        web.find_element(By.ID,'txt_search').clear()
        web.find_element(By.ID,'txt_search').send_keys(KEYWORD,Keys.ENTER)
    
    # while循环实现翻页
    page_count = 0
    while True:
        try:
            page_count += 1
            print(f'{KEYWORD} : 正在读取第{page_count}页!')

            WaitForFive()
            search_results_window_handle = web.current_window_handle
            
            # 获取论文列表
            tr_list = web.find_elements(By.CLASS_NAME,'odd')
            print('trlen:', len(tr_list))
            WaitForFive()
            for tr in tqdm(tr_list):
                item = {}
                # 抓取标题
                try:
                    title = tr.find_element(By.CLASS_NAME,'name').text
                except:
                    title = "无标题"        
                item['title'] = title
                print(title)
                
                #抓取论文链接
                try:
                    link = tr.find_element(By.XPATH, "./td[@class='name']/a").get_attribute('href')
                except:
                    link = ''
                item['link'] = link
                print(link)
                #抓取发表时间
                try:
                    date = tr.find_element(By.XPATH, "./td[@class='date']").text
                except:
                    date = ''
                item['date'] = date
                print(date)

                # 进入详情
                SwitchToDetailWindow(web, link)

                # 抓取摘要
                try:
                    abstract = web.find_element(By.CLASS_NAME, 'abstract-text').text
                except:
                    abstract = "无摘要"
                item['abstract'] = abstract
                print(abstract)

                #抓取关键字
                try:
                    keywords = web.find_elements(By.NAME, 'keyword')
                    keywords_list = []
                    for keyword in keywords:
                        remove_items = r"[.!+-=——,$%^，,。;？?、~@#￥%……&*《》<>「」{}【】()/\\\[\]'\"]"
                        keyword_text = re.sub(remove_items, '', keyword.text)
                        keywords_list.append(keyword_text)
                except:
                    keywords_list = ["无关键词"]
                item['keywords_list'] = keywords_list
                print(keywords_list)
                #抓取作者
                try:
                    author_element = web.find_element(By.ID, 'authorpart')
                    author_elements_list = author_element.find_elements(By.TAG_NAME,'a')
                    author_names_list = []
                    for element in author_elements_list:
                        author_names_list.append(element.text)
                    print(author_names_list)
                except:
                    print("grab author failed")

                #抓取作者从属机构
                wx_tit_element = web.find_element(By.CLASS_NAME, 'wx-tit')
                try:
                    department_element = wx_tit_element.find_element(By.XPATH, './h3[2]')
                    department_elements_list = department_element.find_elements(By.TAG_NAME, 'a')
                except:
                    print("grap department failed")
                department_names_list = []
                for element in department_elements_list:
                    department_names_list.append(element.text)
                print(department_names_list)

                #生成author-department的dict
                author_department_dict = {}
                # 去除非法字符
                r = r"[1234567890 .!+-=——,$%^，,。？?、~@#￥%……&*《》<>「」{}【】()/\\\[\]'\"]"
                for author in author_names_list:
                    for department in department_names_list:
                        # 1:小明1,华南理工大学1 2:小明 华南理工大学
                        if author[-1] == department[0] or author[-1] not in ['0','1','2','3','4','5','6','7','8','9']:
                            author_name = re.sub(r, '', author)
                            department_name = re.sub(r, '', department)
                            author_department_dict[author_name] = department_name
                            break
                item['author_department_dict'] = author_department_dict
                print(item)


                #如果标题中存在/则用汉字替换
                # r = r"[.!+-=——,$%^，,。？?、~@#￥%……&*《》<>「」{}【】()/\\\[\]'\"]"
                # title_copy = re.sub(r, '', title)
                # # 写入爬取信息
                # try:
                #     with open(file_path + '/{0}.txt'.format(title_copy), 'w') as f:
                #         f.write(item)
                # except:
                #     print('文件名称Invalid !')
                print(len(web.window_handles))    
                SwitchToSearchResultWindow(web,search_results_window_handle)
                print('back',len(web.window_handles))
            #本页抓取完毕，点击下一页
            if HasNextPage(web) == True:
                web.find_element(By.ID, 'PageNext').click()
                WaitForTen()
                search_results_window_handle = web.current_window_handle

            else:
                print("have no next page")
                break

        except:
            print('定位失败！当前在第{}页！'.format(page_count))
            # 进入具有搜索栏的页面
            WaitForFive()
            SwitchToSearchResultWindow(web,search_results_window_handle)
            # 点击下一页
            if HasNextPage(web) == True:
                WaitForFive()
                web.find_element(By.ID, 'PageNext').click()
                WaitForFive()
            else:
                print("have no next page")
                break

    print(KEYWORD,'Done!')



if __name__ == '__main__':
    if not os.path.exists('./Data'):
        os.mkdir('./Data')

    opt = Options()
    opt.add_experimental_option('excludeSwitches',['enable-automation'])
    opt.add_argument('--headless')
    opt.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36')
    url = 'https://www.cnki.net/'
    web = Chrome(options=opt)
    web.get(url)
    StartSpider(web)