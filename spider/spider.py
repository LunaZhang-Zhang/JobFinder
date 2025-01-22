# 库使用
# selenium：用于模拟浏览器操作。
# webdriver_manager：自动管理驱动程序。
# BeautifulSoup4：解析HTML页面。

from selenium import webdriver
import logging
import sys
import json
import os
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import urllib.parse
from bs4 import BeautifulSoup


# 岗位信息结构
class JobInfo:
    name = ''          # 岗位名称
    type = ''          # 岗位类别
    location = []      # 工作地点
    company = ''       # 招聘公司
    salary = ''        # 薪资完整信息，我觉得方便用于展示，eg 18-20K*15薪
    min_salary = 0     # 薪资最小值, 为了之后岗位推荐时候查找最低薪资方便
    max_salary = 0     # 薪资最大值
    salary_month = 0
    link = ''          # 岗位链接
    background = ''    # 学历背景
    requirements = ''  # 岗位要求

def random_wait(min_seconds=2, max_seconds=5):
    # 模拟人工，随机等待
    time.sleep(random.uniform(min_seconds, max_seconds))

# 爬虫类
class Spider:
    # 构造函数：类对象初始化
    def __init__(self):
        # 成员变量
        self.driver = None

        # 初始化，配置Edge浏览器驱动
        options = webdriver.EdgeOptions()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')

        try:
            self.driver = webdriver.Edge(options=options)
        except Exception as e:
            logging.error("WebDriver启动失败: %s", e)
            raise SystemExit("请检查网络连接或权限设置。") from e
        self.driver.set_window_size(1920, 1080)


    def __get_cookie(self,url):
        """获取cookies"""
        logging.info("开始获取cookie for %s")
        self.driver.get(url)
        exit_command = input("请在浏览器中完成登录后按回车继续...（输入'exit'并回车以退出）")
        if exit_command.lower() == 'exit':
            logging.info("用户选择退出程序 for %s")
            self.driver.quit()
            sys.exit(0)
        cookies = self.driver.get_cookies()
        cookie_file = f'cookies.json'
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        logging.info("Cookie获取完毕并已保存 for %s")

    def __load_cookies(self):
        """加载cookies"""
        logging.info("开始加载cookie for %s")
        cookie_file = f'cookies.json'
        if not os.path.exists(cookie_file):
            logging.error(f"未找到的cookie文件")
            return False
        self.driver.get("https://www.zhipin.com")  # 确保是cookie对应的域名
        sleep(2)
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
        except IOError as e:
            logging.error(f"读取cookie文件失败: {e}")
            return False
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self.driver.add_cookie(cookie)
        logging.info("Cookie加载完毕 for %s")
        return True


    # 爬取并解析网页,私有方法，私有方法不允许类的外部代码直接调用，但允许类的内部代码调用。
    def __crawl_and_parse(self,base_url) -> list[JobInfo]:
        # 尝试加载指定页面的URL(等待+有限次数的多次尝试)
        job_info_list = []  # 岗位信息列表，本函数的返回
        # 设置爬取最大页数
        MAX_PAGE_NUM = 20
        for page in range(MAX_PAGE_NUM):
            url = f'{base_url}&page={page}'
            is_loaded = False
            for i in range(3):
                try:
                    # 打开目标URL
                    self.driver.get(url)
                    # 等待页面中所有class="job-card-wrapper"的元素加载完成。
                    WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-wrapper")))
                    is_loaded = True
                    break
                except Exception as e:
                    logging.error("尝试 %d 次访问 %s 失败: %s", i + 1, url, e)
                    random_wait((i + 1) * 3, (i + 2) * 3)
            if not is_loaded:
                print("无法加载页面: %s", url)
                return job_info_list

            # 解析网页，提取所需信息
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            jobs = soup.find_all('li', class_='job-card-wrapper')  # name参数用于指定要查找的HTML标签的名称
            # job是一个BeautifulSoup解析后的HTML元素对象, jobs是所有BeautifulSoup解析后的HTML元素对象
            # 一个job对象中包括一个职位所有信息，即'li'标签下的，class='job-card-wrapper'的所有信息，name、area、salary等，所以需要单独提取每个需要的信息
            for job in jobs:
                # 获取每个职位的信息，并添加到列表中
                try:
                    # 1.初始化一个岗位信息对象  2. 获取该对象的岗位信息  3. 把对象添加到岗位信息列表job_info_list，最后返回该列表，存储了爬取到的所有岗位及相关信息
                    job_info_item = JobInfo()
                    job_info_item.name = self.__get_text_from_job(job, ('span', 'job-name'))
                    job_info_item.location = self.__get_text_from_job(job, ('span', 'job-area'))
                    job_info_item.company = self.__get_text_from_job(job, ('h3', 'company-name'))

                    # salary为最小-最大的区间范围，待进一步提取为min_salary、max_salary
                    job_info_item.salary = self.__get_text_from_job(job, ('span', 'salary'))
                    job_info_item.min_salary, job_info_item.max_salary, job_info_item.salary_month = self.__parse_salary_info(job_info_item.salary)

                    # tag_list包括经验要求、学历要求
                    tag_list = [li.text for li in job.find('ul', class_='tag-list').find_all('li')]
                    job_info_item.background = tag_list[1] if len(tag_list) > 1 else ''

                    # 岗位要求信息，从（job-card-footer类）中找到包含标签列表的<ul>元素（tag-list类），然后提取所有的<li>元素的文本内容，并将这些文本用逗号连接成一个字符串。
                    job_info_item.requirements= ','.join([li.text for li in job.find('div', class_='job-card-footer').find('ul', class_='tag-list').find_all('li')])
                    # 岗位详情链接
                    job_info_item.link = "https://www.zhipin.com" + job.find('a')['href']

                    # 直接将字典添加到列表中
                    job_info_list.append(job_info_item)
                except Exception as e:
                    logging.error(f"解析职位信息时出错: {e}")
            random_wait(1, 3)
        return job_info_list


    # 尝试从每个job对象中获取指定选择器的文本
    def __get_text_from_job(self, job, selector):
        try:
            # selector[0]：HTML标签的名称（如 'li'、'div'、'span'、'h3'等）
            # selector[1]：HTML标签的class属性值
            return job.find(name=selector[0], class_=selector[1]).text.strip()
        except AttributeError as e:
            logging.error(f"获取文本时出错: {e}")


    # 将爬取到的薪资信息解析为min_salary、max_salary、salary_month
    def __parse_salary_info(self, salary_text: str) -> tuple[float, float, float]:
        if salary_text == '':
            return 0, 0, 0
        # 去除薪资信息的空格
        salary_text = salary_text.replace(" ", "")  # salary_text='18-20K·15薪'
        # 赋初值
        min_salary, max_salary, salary_month = 0, 0, 12
        # 以K字符分割字符串(不包括K)， split(), 会将字符串分割为两部分，不论是不是以K结尾，所以len(s1)一定>2
        s1 = salary_text.split('K')  # s1=['18-20','·15薪'],
        # 如果salary_text=18K， 则s1=['18',''], 因此需要去掉这种情况下的空字符串, 使用列表推导式或循环来过滤掉空字符串
        s1 = [item for item in s1 if item]
        if len(s1) > 1:
            salary_range = s1[0].split('-')  # salary_range=['18','20']
            min_salary = salary_range[0]
            max_salary = salary_range[1]
        else:
            # 例子：18K
            min_salary = max_salary = s1[0]

        if '薪' in salary_text:
            s2 = salary_text.split('·')  # s2=['18-20k', '15薪']
            s3 = s2[1].split('薪')  # s3=['15', '']
            salary_month = s3[0]

        # 去除空格
        min_salary = str(min_salary).replace(" ", "")
        max_salary = str(max_salary).replace(" ", "")
        salary_month = str(salary_month).replace(" ", "")
        min_salary.replace(" ", "")
        max_salary.replace(" ", "")
        salary_month.replace(" ", "")

        # 以数字返回
        return float(min_salary), float(max_salary), float(salary_month)   # 自动转换成tuple(min_salary, max_salary, month_salary)


    # 存入DB
    def __write_to_database(self, job_info_list: list[JobInfo]) -> None:
        with open("result.json", "w", encoding='utf-8') as file:
            json.dump(job_info_list, file, ensure_ascii=False)
        print('存入DB成功')

    # 爬虫执行器，公有方法，可以被外部代码自由调用。它用于提供类的功能，供其他对象或模块使用。
    def run(self):
        login_url = 'https://www.zhipin.com'
        self.__get_cookie(login_url)
        self.__load_cookies()
        job_query_list = [
            '前端开发', '后端开发', '软件测试', '产品经理', '算法',
            '运维', '数据挖掘', '项目经理', '解决方案'
        ]
        for job_query in job_query_list:
            base_url = 'https://www.zhipin.com/web/geek/job?query={}&city=100010000&experience=102&industry=100020&jobType=1901'.format(
                    urllib.parse.quote(job_query)
                )
            job_info_list = self.__crawl_and_parse(base_url)
            for job_info in job_info_list:
                job_info.type = job_query
            self.__write_to_database(job_info_list)

# 主函数
if __name__ == '__main__':
    Spider().run()
