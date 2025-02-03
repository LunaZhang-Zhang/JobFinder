#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mysql.connector import Error
from web.model import user
from web.model import job
from flask import *
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from flask import request, Blueprint
from flask_jwt_extended import create_access_token
from datetime import timedelta
from web.text_similarity import match_skill_with_requirements

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<htmlname>.html')
def html(htmlname):
    return render_template(htmlname+".html")


# 收藏岗位功能：获取到当前用户ID和收藏的岗位ID，存入数据库
# 1. 根据用户userid，查询数据库，找到该id下的favorite_job_ids(list)
# 2. 添加jobid至favorite_job_id
# 3. 再更新数据库
@app.route("/favoritejob/add", methods=['POST'])
def add_favorite_job():
    param = request.json       # 前端向url为 favoritejob/add 后端接口提交的json字符串
    userid = param['userid']   # 获取json字符串中的 userid
    jobid = param['jobid']     # 获取json字符串中的 jobid
    try:
        # 校验jobid是否存在
        is_job_exist = job.check_job_exist_by_jobid(jobid)
        if not is_job_exist:
            return '收藏的岗位不存在', 400
        # 收藏岗位
        user_info = user.query_user_info_by_userid(userid)
        if user_info is None:
            return '用户不存在。', 400
        user_info.fav_job_ids.append(jobid)
        user.update_fav_job_ids_by_userid(userid, user_info.fav_job_ids)
        return '收藏的岗位已保存。', 200
    except Error as e:
        return f"数据库错误: {e}", 500


# 浏览用户收藏的岗位: 查用户数据库，获取用户收藏的岗位信息，并返回列表
@app.route("/favoritejob/list", methods=['GET'])
def show_favorite_job():
    userid = request.args.get('userid')
    if not userid:
        return "userid 参数缺失", 400
    try:
        fav_job_list = user.query_fav_job_ids_by_userid(userid)
        if len(fav_job_list) == 0:
            return jsonify(result=[]), 200
        job_info_list = job.list_job_info_by_fav_jobid(fav_job_list)
        job_info_list.sort(key=lambda x: x.jobid)
        return jsonify(result=[e.serialize() for e in job_info_list]), 200
    except Error as e:
        return f"数据库错误: {e}", 500


# 取消收藏append->remove
@app.route("/favoritejob/delete", methods=['POST'])
def delete_favorite_job():
    param = request.json
    userid = param['userid']
    jobid = param['jobid']
    try:
        user_info = user.query_user_info_by_userid(userid)
        if user_info is None:
            return '用户不存在。', 400
        if jobid in user_info.fav_job_ids:
            user_info.fav_job_ids.remove(jobid)
            user.update_fav_job_ids_by_userid(userid, user_info.fav_job_ids)
            return '收藏的岗位已删除。', 200
        else:
            return '岗位未收藏。', 400

    except Error as e:
        return f"数据库错误: {e}", 500


@app.route("/matchedjob/list", methods=['POST'])
# 根据用户输入，推荐匹配的岗位信息列表
# 1. 先根据sql查出匹配的所有工作列表, list_job_info_by_user_input(jobType, min_salary, background),
# 通过用户输入的信息（入参:岗位类型、最小薪资、学历背景、个人技能），返回出匹配的岗位信息列表
# 2. 对列表中每条岗位 计算相似度   match_skill_with_requirements(skill, requirements)
# 3. 算完根据相似度从大到小排序返回岗位信息列表
def list_matched_job_info():
    param = request.json
    userid = param.get('userid')
    job_type = param.get('job_type')
    min_salary = param.get('min_salary')
    background = param.get('background')
    skills = param.get('skills')
    # 0. 查询用户感兴趣的job id列表
    user_info = user.query_user_info_by_userid(userid)
    fav_job_ids = user_info.fav_job_ids
    # 1. 根据用户输入，查询匹配的所有工作列表
    raw_job_info_list = job.list_job_info_by_user_input(job_type, min_salary, background)

    # 2. 对列表中每条岗位，计算相似度
    matched_job_info_list = []
    for job_info in raw_job_info_list:
        job_requirements = job_info.requirements  # 假设每个岗位信息中包含一个'requirements'字段
        similarity = match_skill_with_requirements(skills, job_requirements)
        job_info.similarity = similarity  # 将相似度添加到岗位信息中
        # 如果这个岗位id已在该用户的收藏中，则is_favorited = True
        if job_info.jobid in fav_job_ids:
            job_info.is_favorited = True
        matched_job_info_list.append(job_info)

    # 3. 根据相似度从大到小排序返回岗位信息列表
    matched_job_info_list.sort(reverse=True)
    return jsonify(result=[e.serialize() for e in matched_job_info_list]), 200


# 用户注册
@app.route("/user/register", methods=['POST'])
def user_register():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return '用户名或密码不能为空', 400
    else:
        if len(username) < 5:
            return '用户名长度不能小于5位', 400
        if len(password) < 6:
            return '用户名长度不能小于6位', 400

    try:
        user.add_user_info(username, password)
        return '注册成功', 200

    except Error as e:
        return f"数据库错误: {e}", 500


# 用户登录
@app.route("/user/login", methods=['POST'])
def user_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return '用户名或密码不能为空', 400

    try:
        userinfo = user.query_user_info_by_username(username)
        if userinfo.password == password:
            access_token = create_access_token(
                identity=username,
                expires_delta=timedelta(hours=168),
            )
            access_token = f"Bearer {access_token}"
            response = {'token': access_token, 'userid': userinfo.userid}
            return jsonify(response), 200  # token 返回给前端，每次访问时在请求的header里带上
        else:
            return '用户名或密码错误', 400

    except Error as e:
        return f"数据库错误: {e}", 500


# 鉴权
"""
鉴权作用：防止恶意访问，保证除了登录和注册界面，其他界面的访问必须经过登录
实现思路：jwt token，服务端会对登录成功的用户生成一个随机token返回， 之后客户端访问时，会在header中带上token
        eg. {'Authorization', 'token 值'}
"""
# jwt 配置
app.config['JWT_SECRET_KEY'] = 'test'  # 更改为你的密钥
jwt = JWTManager(app)


# 引入路由
auth_blueprint = Blueprint("auth_blueprint", __name__, url_prefix="/user/login")

# 用户登录路由
app.register_blueprint(auth_blueprint)

"""拦截器，所有请求先经过这里，可以获取请求头token进行拦截"""
# 免过滤接口，这里写的是不需要经过jwt token验证的接口，如登录接口或者其他免登接口
exclude_path_patterns_list = ["/user/login", "/user/register", "/"]


@app.before_request
def auth():
    # 获取路径
    url = request.path
    # 如果url在被排除鉴权的url列表内，或静态html，则无需鉴权
    if (url in exclude_path_patterns_list) or (".html" in url):
        return
    try:
        # JWT 验证成功
        verify_jwt_in_request()
    except Exception as e:
        # 如果JWT验证失败，返回错误信息
        return '请登录', 400


if __name__ == "__main__":
    app.run()


