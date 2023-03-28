import pandas as pd
import copy
import re
import requests
from bs4 import BeautifulSoup


# 获取答案
def get_answer(msg):
	cookies = {
		'JSESSIONID': '32CF07517CC47874460C89F75',  # 此处写cookie，请确保和下面的cookie一致
	}
	headers = {
		'Accept': '*/*',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
		'Connection': 'keep-alive',
		'Origin': 'http://172.20.2.22:8080',
		'Referer': 'http://172.20.2.22:8080/SU/practice-test.html',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44',
		'X-Requested-With': 'XMLHttpRequest',
	}

	params = {
		'OPCode': '55',
		'QID': msg[2],
		'QA': f'-1,{msg[1]}',
	}

	response = requests.post('http://172.20.2.22:8080/hello', params=params, cookies=cookies, headers=headers,
	                         verify=False)
	return response.text


# 获取问题
def get_question():
	cookies = {
		'JSESSIONID': '32CF07517CC47874460CC869189F7DD5',  # 此处写cookie，请确保和上面的cookie一致
	}

	headers = {
		"Host": "172.20.2.22:8080",
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53",
		"X-Requested-With": "XMLHttpRequest",
		"Referer": "http://172.20.2.22:8080/SU/practice-test.html"
	}

	data = {
		'OPCode': '53',
		'Simu': '2',
	}

	response = requests.post('http://172.20.2.22:8080/hello', cookies=cookies, headers=headers, data=data, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	divs = soup.find_all('div', class_='qst1_con')
	all_results = []
	result = {}
	for div in divs:
		question = div.find_all('div', class_='qst1_tit')
		# print([i.text.split('、')[1] for i in question][0])
		result["question"] = [i.text.split('、')[1] for i in question][0]
		options = div.find_all('li')
		option_lst = [i.text for i in options]
		onclicks = [input for j in options for input in j.find_all('input', onclick=True)]
		lst = [match.group(0)[:-1] for onclick in onclicks for match in
		       [re.search(r'\(\d+,\d+,\d+\);', onclick['onclick'])] if match]
		for j in range(0, len(lst)):
			if get_answer(eval(lst[j])) == '1':
				# print(option_lst[j])
				result["answer"] = option_lst[j]
		all_results.append(copy.deepcopy(result))
	return all_results


# 将答案数据追加到excel中
def add_data_to_excel(data):
	# 读取excel文件
	df = pd.read_excel('output.xlsx')
	# 将新数据添加到数据框中
	df = df.append(data, ignore_index=True)
	# 将数据写入excel文件
	df.to_excel('output.xlsx', index=False)
	print("Ok!")


if __name__ == '__main__':
	for i in range(300):
		all_results = get_question()
		# 将列表转换为DataFrame
		data = pd.DataFrame(all_results)
		# 将答案数据追加到excel中
		add_data_to_excel(data)
