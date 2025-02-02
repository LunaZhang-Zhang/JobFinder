#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 岗位匹配与展示功能测试
import requests


TEST_USERNAME = 'testUser'
TEST_PASSWORD = 'password123'
test_input_list = []


def get_token_and_userid():
    url_login = "http://127.0.0.1:5000/user/login"
    payload = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    response = requests.post(url_login, data=payload)
    token = response.json()['token']
    userid = response.json()['userid']
    return token, userid


def test_list_matched_job():
    job_type = '后端开发'
    min_salary = 20000
    background = '软件工程'
    skills = 'python'
    token, userid = get_token_and_userid()
    url_list = "http://127.0.0.1:5000/matchedjob/list"
    headers = {
        "Authorization": token,
    }
    payload = {'userid': userid, 'job_type': job_type, 'min_salary': min_salary, 'background': background, 'skills': skills}
    response = requests.post(url_list, json=payload, headers=headers)
    assert response.status_code == 200, f"状态码不正确，预期: 200，实际: {response.status_code}"

    is_satisfied = True
    results = response.json()['result']
    for result in results:
        salary = result['salary']
        result_min_salary =int(salary.split('k')[0])
        print(result_min_salary)
        if not ((result_min_salary > min_salary/1000) and (result['job_type'] == job_type)
               and (result['background'] == '本科' or '硕士' or '')):
            is_satisfied = False
            break
    assert is_satisfied == True


# Todo:
# 1. 数据库唯一键值约束，重新更新岗位模拟数据与用户模拟数据
# 2. 明确min_salary的数值范围，到底存25(k)还是25000，对应的测试代码需要修改 result_min_salary > min_salary/1000
# 3. Q:重新更新了job数据库，数据好像没进去，matched_job_list 查询不到值，test_favorite 添加没有的jobid不会成功，但是不知道咋回事，找不到原因



