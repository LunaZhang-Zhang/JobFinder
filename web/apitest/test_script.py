#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 测试流程脚本
import requests
import data


def get_token_and_userid():
    url_login = "http://127.0.0.1:5000/user/login"
    payload = {"username": data.TEST_USERNAME, "password": data.TEST_PASSWORD}
    response = requests.post(url_login, data=payload)
    token = response.json()['token']
    userid = response.json()['userid']
    return token, userid


def test_api():
    # 1. 登录获取token与userid
    token, userid = get_token_and_userid()
    headers = {
        "Authorization": token,
    }
    # 从 test_cases中获取每个测试用例
    for case in data.TEST_CASES:
        # 2. 将测试用例组装成http请求获取后端响应response
        url = case['url']
        method = case['method']
        payload = case['payload']
        # 给测试用例的payload中赋值真实userid
        if 'userid' in payload.keys():
            payload['userid'] = userid
        response = None
        if method == "GET":
            response = requests.get(url, params=payload, headers=headers)
        elif method == "POST":
            content_type = case['content_type']
            if content_type == "application/json":
                response = requests.post(url, json=payload, headers=headers)
            elif content_type == "application/x-www-form-urlencoded":
                response = requests.post(url, data=payload, headers=headers)
        # 3. 检查status_code是否为目标返回值
        expected_status_code = case['expected']['status_code']
        assert response.status_code == expected_status_code, \
            f"{url} 状态码不正确，预期: {expected_status_code}\n实际: {response.status_code}"
        # 4. 检查response内容是否为目标返回值
        if 'response' in case['expected'].keys():
            expected_response = case['expected']['response']
            assert response.json() == expected_response, \
                f"{url} 预期响应不正确，预期: {expected_response}\n实际: {response.json()}"
