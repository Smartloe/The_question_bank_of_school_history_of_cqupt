## 一、重邮校史答题题库
1、运行时请确保连接学校内网【学校的wifi或vpn】
<br/>
2、代码需要填入自己的cookie【就是校史答题页面的cookie】
<br/>
3、此脚本是通过不断刷新测试题来构建的题库，因此运行效率低。
<br/>
4、其中`output.xlsx`文件是我运行代码收集的题库，但是有缺少。【如希望获取完整的可自行运行脚本收集！】
<br/>
5、希望有兴趣的朋友可以在此代码的基础上加以完善！【如加上异步等】
<br/>
6、自动考试脚本答案是基于output.xlsx题库的，因此可能有不准确的地方，如有问题请自行修改！

## 二、关于自动答题

1、关于JSESSIONID的获取

先在[校史校情一点通](http://172.20.2.22:8080/index/index.html)进行登录，使用`F12`或`Fn+F12`打开控制台，然后选择`网路`那个Tab,最后刷新网页，随便选一个请求查看cookie，复制JSESSIONID。如下图所示：

![image](https://raw.githubusercontent.com/Smartloe/The_question_bank_of_school_history_of_cqupt/main/img/QQ_1720341542579.png)

2、关于脚本运行

脚本有两个版本，一个纯代码版，一个是GUI版。小白的话点击下载[GUI版](https://github.com/Smartloe/The_question_bank_of_school_history_of_cqupt/releases/tag/answer)中的`automatic._answer1.0.zip`，解压后双击运行，填入刚才复制的JSESSIONID即可。
