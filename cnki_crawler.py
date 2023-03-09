import os
import re
import time
import csv

from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from datetime import datetime

def WaitForFive():
    time.sleep(5)

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
        WaitForFive()
    except:
        print("switch to search result window failed")

# 爬取数据
def StartSpider(web, keyword, grab_pages_number = 3, continue_last_grab = False, continue_search_result_page_number = 0):

    page_count = continue_search_result_page_number

    if continue_last_grab == False:
        #重新从头抓取
        global KEYWORD
        KEYWORD = keyword
        WaitForFive()
        try:
            #主页搜索
            web.find_element(By.ID,"txt_SearchText").send_keys(KEYWORD,Keys.ENTER)
            
        except:
            #非主页搜索
            web.find_element(By.ID,'txt_search').clear()
            web.find_element(By.ID,'txt_search').send_keys(KEYWORD,Keys.ENTER)
    
    for grab_step in range (0, grab_pages_number):
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
                
                #抓取论文链接
                try:
                    link = tr.find_element(By.XPATH, "./td[@class='name']/a").get_attribute('href')
                except:
                    link = ''
                item['link'] = link

                #抓取发表时间
                try:
                    date = tr.find_element(By.XPATH, "./td[@class='date']").text
                except:
                    date = ''
                item['date'] = date

                #记录爬取时间
                now = datetime.now() # 获取当前时间
                retrieve_time = now.strftime("%Y-%m-%d %H:%M:%S") # 将时间格式化为字符串
                item['retrieve_time'] = retrieve_time

                # 进入详情
                SwitchToDetailWindow(web, link)

                # 抓取摘要
                try:
                    abstract = web.find_element(By.CLASS_NAME, 'abstract-text').text
                except:
                    abstract = "无摘要"
                item['abstract'] = abstract

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

                #抓取作者
                try:
                    author_element = web.find_element(By.ID, 'authorpart')
                    author_elements_list = author_element.find_elements(By.TAG_NAME,'a')
                    author_names_list = []
                    for element in author_elements_list:
                        author_names_list.append(element.text)
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

                # 打开 CSV 文件，使用 utf-8-sig 编码以支持中文
                csv_filename = 'Data.csv'
                # check if the CSV file exists
                if not os.path.isfile(csv_filename):
                    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        # 写入标题行
                        writer.writerow(['title', 'author', 'department', 'keywords', 'abstract', 'published_date', 'url', 'retrieve_time'])
                # append data to the CSV file 
                with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    # 写入数据行
                    # 遍历作者字典，获取每个作者的名称和单位
                    for author, department in author_department_dict.items():
                        keywords_str = "|".join(keywords_list)
                        writer.writerow([title, author, department, keywords_str, abstract, date, link, retrieve_time])

                SwitchToSearchResultWindow(web,search_results_window_handle)
                print('back',len(web.window_handles))

            #本页抓取完毕，点击下一页
            if HasNextPage(web) == True:
                web.find_element(By.ID, 'PageNext').click()
                WaitForFive()
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
    StartSpider(web,"人工智能",1)
    StartSpider(web,"人工智能",1,True,1)