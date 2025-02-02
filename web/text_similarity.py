#!/usr/bin/env python
# -*- coding:utf-8 -*-

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# skill与requirements匹配, 返回一个匹配度的值
def match_skill_with_requirements(skill_text:str, requirements_text:str) -> float:
    # 1. skill_text 与 requirements_text 做分词
    # 使用 jieba 进行分词
    text1_cut = " ".join(jieba.cut(skill_text))
    text2_cut = " ".join(jieba.cut(requirements_text))
    # 将分词后的文本放入列表中
    corpus = [text1_cut, text2_cut]

    # 2. 计算分词后的俩文本相似度
    # 使用 TfidfVectorizer 计算 TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    # 计算两个文本的余弦相似度
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return similarity[0][0]