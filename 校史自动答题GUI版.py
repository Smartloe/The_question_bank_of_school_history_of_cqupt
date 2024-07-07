import wx
import requests
import pandas as pd
import random
import time
import threading


class ExamFrame(wx.Frame):
	def __init__(self):
		super().__init__(None, title='CQUPT校史自动答题', size=(800, 600))

		# 设置窗口图标
		icon = wx.Icon('img/logo.png', wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.panel = wx.Panel(self)
		self.create_widgets()

		self.thread = None  # 线程对象

	def create_widgets(self):
		vbox_main = wx.BoxSizer(wx.VERTICAL)

		# 标题
		font_title = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
		title = wx.StaticText(self.panel, label='CQUPT校史自动答题', style=wx.ALIGN_CENTER)
		title.SetFont(font_title)
		vbox_main.Add(title, 0, wx.ALL | wx.EXPAND, 20)

		# 输入JSESSIONID部分
		hbox_jsessionid = wx.BoxSizer(wx.HORIZONTAL)
		self.lbl_jsessionid = wx.StaticText(self.panel, label='JSESSIONID：')
		hbox_jsessionid.Add(self.lbl_jsessionid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
		self.txt_jsessionid = wx.TextCtrl(self.panel)
		hbox_jsessionid.Add(self.txt_jsessionid, 1, wx.EXPAND | wx.ALL, 10)
		self.btn_submit_jsessionid = wx.Button(self.panel, label='提交')
		self.btn_submit_jsessionid.Bind(wx.EVT_BUTTON, self.submit_jsessionid)
		hbox_jsessionid.Add(self.btn_submit_jsessionid, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
		vbox_main.Add(hbox_jsessionid, 0, wx.EXPAND)

		# 开始答题和停止答题按钮
		hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_start_exam = wx.Button(self.panel, label='开始答题', style=wx.BU_EXACTFIT)
		self.btn_start_exam.Bind(wx.EVT_BUTTON, self.start_exam)
		hbox_buttons.Add(self.btn_start_exam, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

		self.btn_stop_exam = wx.Button(self.panel, label='停止答题', style=wx.BU_EXACTFIT)
		self.btn_stop_exam.Bind(wx.EVT_BUTTON, self.stop_exam)
		self.btn_stop_exam.Disable()  # 初始时停止按钮禁用
		hbox_buttons.Add(self.btn_stop_exam, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
		vbox_main.Add(hbox_buttons, 0, wx.ALIGN_LEFT)

		# 输出框
		self.output_box = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
		vbox_main.Add(self.output_box, 1, wx.EXPAND | wx.ALL, 10)

		self.panel.SetSizer(vbox_main)
		self.Layout()

	def submit_jsessionid(self, event):
		self.session_id = self.txt_jsessionid.GetValue().strip()
		if self.session_id:
			self.btn_submit_jsessionid.Disable()
			self.btn_start_exam.Enable()
			wx.MessageBox('JSESSIONID提交成功！', '信息', wx.OK | wx.ICON_INFORMATION)
		else:
			wx.MessageBox('请输入有效的JSESSIONID！', '警告', wx.OK | wx.ICON_WARNING)

	def start_exam(self, event):
		self.output_box.Clear()  # 清空输出框

		self.btn_start_exam.Disable()
		self.btn_stop_exam.Enable()

		self.thread = threading.Thread(target=self.perform_exam)
		self.thread.start()

	def stop_exam(self, event):
		if self.thread and self.thread.is_alive():
			self.thread.do_run = False
			self.btn_stop_exam.Disable()

	def perform_exam(self):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
		}
		cookies = {
			'JSESSIONID': self.session_id,
		}

		def get_formal_questions():
			url = 'http://172.20.2.22:8080/index/examination/getFormalQuestions'
			response = requests.get(url, headers=headers, cookies=cookies, verify=False)
			return response.json()

		def get_answers_from_excel(filename='output.xlsx'):
			try:
				df = pd.read_excel(filename)
				answers_dict = df.set_index('QID')['CorrectAnswer'].to_dict()
				return answers_dict
			except FileNotFoundError:
				wx.CallAfter(self.output_box.AppendText, f"文件 {filename} 不存在。\n")
				return {}

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

		def submit_answer(qid, answer):
			url = 'http://172.20.2.22:8080/index/examination/saveFormalAnswer'
			data = {
				'QID': qid,
				'answer': answer,
			}
			response = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False)
			return response.json()

		def finish_formal_test():
			url = 'http://172.20.2.22:8080/index/examination/finishFormalTest'
			response = requests.post(url, headers=headers, cookies=cookies, verify=False)
			return response.json()

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
				your_score = f"{latest_score['UserName']}同学，你的最新成绩为: {latest_score['Score']}分, {'恭喜通过' if latest_score['Passed'] else '很遗憾未通过'}。\n"

				return your_score

			except requests.exceptions.RequestException as e:
				wx.CallAfter(self.output_box.AppendText, f"获取成绩时发生错误: {e}\n")
				return None

		questions_data = get_formal_questions()
		if 'data' not in questions_data or 'questionList' not in questions_data['data']:
			wx.CallAfter(self.output_box.AppendText, "获取考试试题失败。\n")
			return

		questions = questions_data['data']['questionList']
		answers_dict = get_answers_from_excel('output.xlsx')
		if not answers_dict:
			wx.CallAfter(self.output_box.AppendText, "从文件中获取答案失败。\n")
			return

		for mq in match_answers(questions, answers_dict):
			if self.thread and getattr(self.thread, 'do_run', True):
				if mq['CorrectAnswerAVal'] is not None:
					result = submit_answer(mq['QID'], mq['CorrectAnswerAVal'])
					wx.CallAfter(self.output_box.AppendText,
					             f"题目: {mq['QContent']}\n正确答案: {mq['CorrectAnswer']}\nSubmission Result: {result['msg']}\n\n")
					delay = random.uniform(1, 10)
					time.sleep(delay)
				else:
					wx.CallAfter(self.output_box.AppendText, f"题目: {mq['QContent']}\n没有找到匹配的答案。\n\n")

		if getattr(self.thread, 'do_run', True):
			if self.thread:
				finish_formal_test()
				score = get_latest_score()
				if score:
					wx.CallAfter(self.output_box.AppendText, score)

		wx.CallAfter(self.btn_start_exam.Enable)
		wx.CallAfter(self.btn_stop_exam.Disable)


if __name__ == '__main__':
	app = wx.App()
	frame = ExamFrame()
	frame.Show()
	app.MainLoop()
