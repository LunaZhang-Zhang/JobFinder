#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 收藏功能测试
import requests

TEST_USERNAME = 'testUser'
TEST_PASSWORD = 'password123'


def get_token_and_userid():
    url_login = "http://127.0.0.1:5000/user/login"
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(url_login, data=payload)
    token = response.json()['token']
    userid = response.json()['userid']
    return token, userid


def add_favorite(token, userid, jobid):
    url_add = "http://127.0.0.1:5000/favoritejob/add"
    headers = {
        "Authorization": token,
    }
    payload = {'userid': userid, 'jobid': jobid}
    response = requests.post(url_add, json=payload, headers=headers)
    return response


def delete_favorite(token, userid, jobid):
    url_delete = "http://127.0.0.1:5000/favoritejob/delete"
    headers = {
        "Authorization": token,
    }
    payload = {'userid': userid, 'jobid': jobid}
    response = requests.post(url_delete, json=payload, headers=headers)
    return response


def list_favorite(token, userid):
    url_list = "http://127.0.0.1:5000/favoritejob/list"
    headers = {
        "Authorization": token,
    }
    payload = {'userid': userid}
    response = requests.get(url_list, params=payload, headers=headers)
    return response


def test_favorite():
    token, userid = get_token_and_userid()
    jobid = 88
    response_add = add_favorite(token, userid, jobid)
    assert response_add.status_code == 200, f"状态码不正确，预期: 200，实际: {response_add.status_code}"

    response_list = list_favorite(token, userid)
    assert response_list.status_code == 200, f"状态码不正确，预期: 200，实际: {response_list.status_code}"
    ''' json
        {
            "result": [
                {
                  "jobid": 1,
                  ...  
                },
                {
                  "jobid": 2,
                  ...  
                },
            ]
        }
    '''
    is_added = False  # is_added 是一个布尔变量，用于标记指定的 jobid 是否已经成功添加到收藏列表中。
    results = response_list.json()['result']  # results: [{jobid: 1, ...}, {jobid:2, ...}, ...]
    # 检查 favoritejob/list 返回的收藏列表,看jobid是否被加入（遍历列表中每个岗位，检查其id是否为新收藏的的jobid（20））
    # 如果添加了虚无的jobid，list返回的jobid为空，则会报错
    for result in results:
        if result['jobid'] == jobid:
            is_added = True
            break
    assert is_added == True   # 如果 is_added 为 True，说明目标 jobid 已经成功添加到收藏列表中，测试通过。

    # 删除功能测试
    response_del = delete_favorite(token, userid, jobid)
    assert response_del.status_code == 200

    response_list = list_favorite(token, userid)
    assert response_list.status_code == 200, f"状态码不正确，预期: 200，实际: {response_del.status_code}"
    is_not_deleted = True
    results = response_list.json()['result']  # results: [{jobid: 1, ...}, {jobid:2, ...}, ...]
    for result in results:
        if result['jobid'] == jobid:
            is_not_deleted = False
            break
    assert is_not_deleted == False


def test_add_favorite_abnormal():   # 收藏功能测试(异常情况)
    token, userid = get_token_and_userid()
    jobid = 300
    response_add = add_favorite(token, userid, jobid)
    assert response_add.status_code == 400, f"状态码不正确，预期: 400，实际: {response_add.status_code}"


def test_delete_favorite_abnormal():   # 删除功能测试(异常情况)
    token, userid = get_token_and_userid()
    jobid = 0  # 测试异常删除, 删除有未收藏岗位
    response_del = delete_favorite(token, userid, jobid)
    assert response_del.status_code == 400, f"状态码不正确，预期: 400，实际: {response_del.status_code}"







