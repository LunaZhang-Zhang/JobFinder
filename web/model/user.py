#!/usr/bin/env python
# -*- coding:utf-8 -*-

import mysql.connector
from mysql.connector import Error
from typing import List
from .database import db_config


# 用户信息结构
class UserInfo:
    userid = 0
    username = ''
    password = ''
    fav_job_ids = []

    def __init__(self, db_query_result):
        self.userid = db_query_result['ID']
        self.username = db_query_result['username']
        self.password = db_query_result['password']
        # raw_fav_job_ids：数据库中原始存储的收藏岗位的列表，为字符串类型，以','分割
        # 1. 以','分割字符串，为字符串列表  eg. ['1','2','5']
        # 2. 将字符串列表转化为int型列表：提取列表中每个字符串，转成int型，再放入列表
        # 3. set()去重，再转换为list列表
        raw_fav_job_ids = db_query_result['favorite_job_ids']
        if not raw_fav_job_ids:
            return
        fav_job_str_ids = raw_fav_job_ids.split(',')
        for fav_job_str_id in fav_job_str_ids:
            fav_job_id = int(fav_job_str_id)
            self.fav_job_ids.append(fav_job_id)
        self.fav_job_ids = list(set(self.fav_job_ids))   # list[int]


# 输入用户id，查询用户信息，返回UserInfo对象
def query_user_info_by_userid(userid):
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(host=db_config['host'],port=db_config['port'],user=db_config['user'],
                                       passwd=db_config['password'],database=db_config['database'])
        mydb.autocommit = True
        cursor = mydb.cursor(dictionary=True, buffered=True)  # 以字典返回

        # 执行查询语句
        query_sql = "SELECT * FROM user WHERE ID = %s;"
        cursor.execute(query_sql, (userid,))  # 传递一个包含所有参数的元组,所以一个元素也得用（，）
        result = cursor.fetchone()  # 返回一个元组（tuple）, 一行数据

        # 直接返回UserInfo对象（入参：result）
        return UserInfo(result)

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


# 输入用户id、更新后的favorite_job_ids, 将新的favorite_job_ids写入数据库
def update_fav_job_ids_by_userid(userid, updated_favorite_job_ids: List[int]):
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(host=db_config['host'],port=db_config['port'],user=db_config['user'],
                                       passwd=db_config['password'],database=db_config['database'])
        cursor = mydb.cursor(dictionary=True)

        # 更新数据库中的 favorite_job_ids
        update_sql = "UPDATE user SET favorite_job_ids = %s WHERE ID = %s"
        cursor.execute(update_sql, (",".join(str(i) for i in list(set(updated_favorite_job_ids))), userid))
        mydb.commit()
        print("岗位收藏列表已更新。")

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


# 根据用户id，查询favorite_job_ids并返回(返回favorite_job_ids（list[int]）)
def query_fav_job_ids_by_userid(userid):
    return query_user_info_by_userid(userid).fav_job_ids


# 在数据库中新增用户信息
def add_user_info(username, password):
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(host=db_config['host'], port=db_config['port'], user=db_config['user'],
                                       passwd=db_config['password'], database=db_config['database'])
        cursor = mydb.cursor(dictionary=True)

        # 数据库插入新用户信息
        insert_sql = "INSERT INTO user (username, password) VALUES (%s, %s)"
        cursor.execute(insert_sql, (username, password))
        mydb.commit()
        print("用户信息已保存。")

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


# 基于用户名查询用户信息
def query_user_info_by_username(username):
    mydb = None
    cursor = None
    try:
        mydb = mysql.connector.connect(host=db_config['host'], port=db_config['port'], user=db_config['user'],
                                       passwd=db_config['password'], database=db_config['database'])
        cursor = mydb.cursor(dictionary=True)  # 以字典返回

        # 执行查询语句
        query_sql = "SELECT * FROM user WHERE username = %s;"
        cursor.execute(query_sql, (username,))  # 传递一个包含所有参数的元组,所以一个元素也得用（，）
        result_pwd = cursor.fetchone()
        # 返回一个元组（tuple）, 一行数据, 字典形式 eg. {'password':'123456'}，需要提取出来
        return UserInfo(result_pwd)

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