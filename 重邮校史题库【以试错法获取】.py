import pandas as pd
import requests

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',

}


# 获取题目
def get_question():
	url = 'http://172.20.2.22:8080/index/examination/getTestQuestions'

	cookies = {
		'JSESSIONID': 'D833FCE7C3C3DD7DF56E804C0CF002AE',
	}

	response = requests.get(url, headers=headers, cookies=cookies, verify=False)

	return response.json()
