# -*- coding: utf-8 -*-
"""
@Author: Chenxr
@Date:   2024/6/22 22:24
@Last Modified by:   Chenxr
@Last Modified time: 2024/6/22 22:24
@Description:
"""
import requests
import pandas as pd
import time
import random

# 请求头和Cookies
headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
}
cookies = {
	'JSESSIONID': '20F13F9A11437D790D0B8D9C97AF589A',  # 此处填写你的JSESSIONID，在考试网页中可以通过浏览器开发者工具查看
}


# 获取考试试题
def get_formal_questions():
	url = 'http://172.20.2.22:8080/index/examination/getFormalQuestions'
	response = requests.get(url, headers=headers, cookies=cookies, verify=False)
	return response.json()


# 从output.xlsx中获取答案
def get_answers_from_excel(filename='output.xlsx'):
	try:
		df = pd.read_excel(filename)
		answers_dict = df.set_index('QID')['CorrectAnswer'].to_dict()
		return answers_dict
	except FileNotFoundError:
		print(f"文件 {filename} 不存在。")
		return {}


# 根据试题数据匹配答案
def match_answers(questions, answers_dict):
	matched_questions = []
	for question in questions:
		qid = question['QID']
		qcontent = question['QContent']
		correct_answer_text = answers_dict.get(qid, None)
		correct_answer_aval = None
		if correct_answer_text:
			for answer in question['answers']:
				if answer['AText'] == correct_answer_text:
					correct_answer_aval = answer['AVal']
					break
		matched_questions.append({
			'QID': qid,
			'QContent': qcontent,
			'CorrectAnswer': correct_answer_text,
			'CorrectAnswerAVal': correct_answer_aval
		})
	return matched_questions


# 提交答案
def submit_answer(qid, answer):
	url = 'http://172.20.2.22:8080/index/examination/saveFormalAnswer'
	data = {
		'QID': qid,
		'answer': answer,
	}
	response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False)
	return response.json()


# 提交完成考试请求
def finish_formal_test():
	url = 'http://172.20.2.22:8080/index/examination/finishFormalTest'
	response = requests.post(url, headers=headers, cookies=cookies, verify=False)
	return response.json()


# 查看成绩
def get_latest_score():
	url = 'http://172.20.2.22:8080/index/examination/myScore'

	params = {
		'page': '1',
		'limit': '20',
		'type': '0'
	}
	try:
		response = requests.get(url, headers=headers, cookies=cookies, params=params, verify=False)
		response.raise_for_status()  # 抛出异常以处理不良状态码

		# 提取成绩列表
		scores = response.json()['data']['list']

		# 按照考试时间降序排序，获取最新的成绩
		latest_score = max(scores, key=lambda x: x['TestTime'])

		# 转换"Passed"字段为布尔值
		latest_score['Passed'] = bool(latest_score['Passed'])
		your_score = f"{latest_score['UserName']}同学，你的最新成绩为: {latest_score['Score']}分, {'恭喜通过' if latest_score['Passed'] else '很遗憾未通过'}。"

		return your_score

	except requests.exceptions.RequestException as e:
		print(f"获取成绩时发生错误: {e}")
		return None


if __name__ == '__main__':
	questions_data = get_formal_questions()
	questions = questions_data['data']['questionList']
	answers_dict = get_answers_from_excel('output.xlsx')
	matched_questions = match_answers(questions, answers_dict)
	# 开始做题
	for mq in matched_questions:
		if mq['CorrectAnswerAVal'] is not None:
			result = submit_answer(mq['QID'], mq['CorrectAnswerAVal'])
			print(f"题目: {mq['QContent']}\n正确答案: {mq['CorrectAnswer']}\nSubmission Result: {result['msg']}\n")
			# 随机延迟1到10秒
			delay = random.uniform(1, 10)
			time.sleep(delay)
		else:
			print(f"题目: {mq['QContent']}\n没有找到匹配的答案。\n")
	# 交卷
	finish_formal_test()
	# 获取最新成绩
	print(get_latest_score())
