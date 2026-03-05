2026-1-29
这个版本可以正常部署
1.rustfs里面要创建存储桶club-interview并设置访问策略为公有，并上传文件production/clubs/logos/club-logo-default.png和dev/clubs/logos/club-logo-default.png
2.mysql数据库要先建好，数据库名称campus_club_interview，建库和表的sql在sql文件夹里面，部份表在创建的时候会自动插入数据（例如school表），sql文件夹不要上传到服务器上
3.宝塔面板里面：
    启动文件：选择 app/main.py
    运行端口：8000
    Python 版本：3.10+
    在服务器ssh里先安装好环境：pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    启动方式：选择 Gunicorn
4.环境变量从文件加载，先把.env.production改成.env，然后设置环境变量文件为.env