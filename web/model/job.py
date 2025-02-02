#!/usr/bin/env python
# -*- coding:utf-8 -*-

import mysql.connector
from mysql.connector import Error
from typing import List
from .database import db_config


# 岗位信息结构 注意与SQL的属性区分
class JobInfo:
    jobid = 0
    name = ''          # 岗位名称
    job_type = ''      # 岗位类别
    location = []      # 工作地点
    company = ''       # 招聘公司
    salary = ''        # 薪资完整信息，我觉得方便用于展示，eg 18-20K*15薪
    min_salary = 0     # 薪资最小值, 为了之后岗位推荐时候查找最低薪资方便
    max_salary = 0     # 薪资最大值
    salary_month = 0   # 薪资月数
    link = ''          # 岗位链接
    background = ''    # 学历背景
    requirements = ''  # 岗位要求
    is_favorited = False   # 该岗位是否被对应用户收藏
    similarity = 0     # 岗位requirement与个人skills的匹配度

    def __init__(self, db_query_result):
        self.jobid = db_query_result['ID']
        self.name = db_query_result['name']
        self.job_type = db_query_result['type']
        self.location = db_query_result['location']
        self.company = db_query_result['company']
        self.salary = db_query_result['salary']
        self.link = db_query_result['link']
        self.background = db_query_result['background']
        self.requirements = db_query_result['requirements']

    def serialize(self):   # 转换成json格式
        return {
            'jobid': self.jobid,
            'name': self.name,
            'job_type': self.job_type,
            'location': self.location,
            'company': self.company,
            'salary': self.salary,
            'link': self.link,
            'background': self.background,
            'requirements': self.requirements,
            'is_favorited': self.is_favorited,
        }


# 根据jobid查询job是否存在，返回bool值
def check_job_exist_by_jobid(jobid:int):
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(host=db_config['host'], port=db_config['port'], user=db_config['user'],
                                       passwd=db_config['password'], database=db_config['database'])
        cursor = mydb.cursor(dictionary=True, buffered=True)
        # 动态生成 IN 子句的占位符
        query_sql = f"SELECT * FROM job WHERE ID = %s"
        # 执行查询
        cursor.execute(query_sql, (jobid,))
        result = cursor.fetchone()  # 获取查询结果

        if result is None:
            return False
        return True

    except Error as e:
        print(f"数据库错误: {e}")
        raise e
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if mydb and mydb.is_connected():
            mydb.close()
            print("数据库连接已关闭。")


# 根据favorite_job_ids(list)，返回所有收藏的岗位信息（list[JobInfo]）
def list_job_info_by_fav_jobid(favorite_job_ids: List[int]):
    mydb = None
    cursor = None
    job_list = []
    try:
        mydb = mysql.connector.connect(host=db_config['host'], port=db_config['port'], user=db_config['user'],
                                       passwd=db_config['password'], database=db_config['database'])
        cursor = mydb.cursor(dictionary=True, buffered=True)
        # 动态生成 IN 子句的占位符
        placeholders = ', '.join(['%s'] * len(favorite_job_ids))
        query_sql = f"SELECT * FROM job WHERE ID IN ({placeholders})"
        # 执行查询
        cursor.execute(query_sql, favorite_job_ids)
        results = cursor.fetchall()  # 获取所有查询结果

        for result in results:  # 每条结果都是一个岗位信息对象
            job_info = JobInfo(result)
            job_list.append(job_info)
        return job_list  # 返回一个包含所有 JobInfo 对象的列表

    except Error as e:
        print(f"数据库错误: {e}")
        raise e
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if mydb and mydb.is_connected():
            mydb.close()
            print("数据库连接已关闭。")


# 根据用户输入（jobType, min_salary, background），返回岗位信息
def list_job_info_by_user_input(job_type, min_salary, background):
    mydb = None
    cursor = None
    job_list = []
    try:
        mydb = mysql.connector.connect(host=db_config['host'], port=db_config['port'], user=db_config['user'],
                                       passwd=db_config['password'], database=db_config['database'])
        cursor = mydb.cursor(dictionary=True, buffered=True)

        if background == '硕士':
            background = '本科, 硕士'
        if background == '博士':
            background = '本科, 硕士, 博士'

        # 执行查询语句
        query_sql = """
            SELECT * FROM job 
            WHERE type = %s 
            AND min_salary > %s
            AND background like %s
            """
        cursor.execute(query_sql, (job_type, min_salary, f'%{background}%'))
        results = cursor.fetchall()

        for result in results:  # 每条结果都是一个岗位信息对象
            job_info = JobInfo(result)
            job_list.append(job_info)
        return job_list  # 返回一个包含所有 JobInfo 对象的列表

    except Error as e:
        print(f"数据库错误: {e}")
        raise e
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if mydb and mydb.is_connected():
            mydb.close()
            print("数据库连接已关闭。")
