import multiprocessing

bind = "cut_pdf:5000"
workers = int(multiprocessing.cpu_count()*1.3)+1
chdir = "/home/cut_pdf/RECEIPT"
wsgi_app = "wsgi:app"
loglevel = 'info'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"  "%(a)s"'
accesslog = "cut_pdf-gunicorn.log"
proc_name = 'CUT_PDF'
# Перезапуск после N кол-во запросов
max_requests = 0
# Перезапуск, если ответа не было более 60 сек
timeout = 60
# umask or -m 007
umask = 0x007
# Проверка IP адресов, с которых разрешено обрабатывать набор безопасных заголовков
forwarded_allow_ips = '10.51.203.165,10.51.203.167,127.0.0.1'
#preload увеличивает производительность - хуже uwsgi!
#preload_app = 'True'
