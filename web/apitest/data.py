#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 测试配置文件
TEST_USERNAME = 'testUser'
TEST_PASSWORD = 'password123'

TEST_CASES = [
    # 测试收藏功能（正常情况）
    {
        'url': 'http://127.0.0.1:5000/favoritejob/add',
        'method': 'POST',        # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,   # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'jobid': 88
        },
        'expected': {
            'status_code': 200,
            # 'response': '',
        }
    },
    # 测试浏览功能，并通过浏览功能的返回确定收藏功能是否添加成功
    {
        'url': 'http://127.0.0.1:5000/favoritejob/list',
        'method': 'GET',        # http 请求方法
        'payload': {
            'userid': -1,   # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
        },
        'expected': {
            'status_code': 200,
            'response': {
                "result": [
                    {
                        "background": "硕士",
                        "company": "小米",
                        "is_favorited": False,
                        "job_type": "项目经理",
                        "jobid": 88,
                        "link": "https://www.xiaomi.com",
                        "location": "深圳",
                        "name": "项目经理",
                        "requirements": "具备团队管理经验",
                        "salary": "32k-42k"
                    }
                ]
            }
        }
    },
    # 测试删除功能（正常情况）
    {
        'url': 'http://127.0.0.1:5000/favoritejob/delete',
        'method': 'POST',  # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,  # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'jobid': 88
        },
        'expected': {
            'status_code': 200,
            # 'response': '',
        }
    },
    # 删除功能测试(异常情况)，测试删除不存在岗位
    {
        'url': 'http://127.0.0.1:5000/favoritejob/delete',
        'method': 'POST',  # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,  # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'jobid': 1
        },
        'expected': {
            'status_code': 400,
            # 'response': '',
        }
    },
    # 收藏功能测试(异常情况)，测试收藏不存在岗位
    {
        'url': 'http://127.0.0.1:5000/favoritejob/add',
        'method': 'POST',        # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,   # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'jobid': 1
        },
        'expected': {
            'status_code': 400,
            # 'response': '',
        }
    },
    # 岗位匹配功能测试
    {
        'url': 'http://127.0.0.1:5000/matchedjob/list',
        'method': 'POST',        # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,   # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'job_type': '后端开发',
            'min_salary': 20000,
            'background': '本科',
            'skills': 'python'
        },
        'expected': {
            'status_code': 200,
            'response': {
                'result': [
                    {
                        'background': '本科',
                        'company': '滴滴出行',
                        'is_favorited': False,
                        'job_type': '后端开发',
                        'jobid': 91,
                        'link': 'https://www.didichuxing.com',
                        'location': '广州',
                        'name': '后端开发工程师',
                        'requirements': '熟悉Python',
                        'salary': '24k-34k'
                    },
                    {
                        'background': '本科',
                        'company': '京东',
                        'is_favorited': False,
                        'job_type': '后端开发',
                        'jobid': 118,
                        'link': 'https://www.jd.com',
                        'location': '上海',
                        'name': '后端开发工程师',
                        'requirements': '熟悉Ruby语言',
                        'salary': '25k-35k'
                    },
                    {
                        'background': '本科',
                        'company': '滴滴出行',
                        'is_favorited': False,
                        'job_type': '后端开发',
                        'jobid': 109,
                        'link': 'https://www.didichuxing.com',
                        'location': '北京',
                        'name': '后端开发工程师',
                        'requirements': '熟悉Go语言',
                        'salary': '24k-34k'
                    },
                    {
                        'background': '本科',
                        'company': '京东',
                        'is_favorited': False,
                        'job_type': '后端开发',
                        'jobid': 100,
                        'link': 'https://www.jd.com',
                        'location': '深圳',
                        'name': '后端开发工程师',
                        'requirements': '熟悉Node.js',
                        'salary': '25k-35k'
                    },
                    {
                        'background': '本科',
                        'company': '阿里巴巴',
                        'is_favorited': False,
                        'job_type': '后端开发',
                        'jobid': 82,
                        'link': 'https://www.alibaba.com',
                        'location': '上海',
                        'name': '后端开发工程师',
                        'requirements': '熟悉Java、Spring框架',
                        'salary': '25k-35k'
                    }
                ]
            },
        }
    },
    # 岗位匹配功能测试(异常情况)
    {
        'url': 'http://127.0.0.1:5000/matchedjob/list',
        'method': 'POST',        # http 请求方法
        'content_type': 'application/json',  # 负载格式
        'payload': {
            'userid': -1,   # 此处userid为占位符，真实userid应等待测试运行时获取token时得到再赋值
            'job_type': '后端开发',
            'min_salary': 20000000,
            'background': '本科',
            'skills': 'python'
        },
        'expected': {
            'status_code': 200,
            'response': {
                'result': []
            }
        }
    }
]
