#!/usr/bin/env python
# coding:utf8

import os
import time
import logging
import socket
import threading
from package import connect
from package import load_shell
from package import get_ip_list
from package import logging
from package import get_region

# touch log file
if not os.path.isdir('./log/init_log/'):os.makedirs('./log/init_log/')
# log format
logname='./log/init_log/system_init-%s.log' % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))

logging = logging.log(logname)

print("log output in {}".format(logname))

# init
gs_local_dir=r'/home/deploy-pags/gs-android'
gs_remote_dir=r'/sdcard/gs-android'
gs_init_list=[]
#gs_init_list.append('tools/Q8Box/enable_system_app.sh')
gs_init_list.append('tools/Q8Box/disable_system_app.sh')
gs_init_list.append('tools/Q8Box/init_system.sh')
gs_init_list.append('game/Q8L_3288_100948_GAMES/18.MengHuanHuaYuan/ArchiveFile.sh')
ip_list = get_ip_list.get_ip_list()
action_list = []

# Upload the installation package
def setup_gs_android(ip):
    logging.info('{} push gs-android'.format(ip))
    status,stdout = load_shell.shell('adb -s {}:5555 push {} {}'.format(ip,gs_local_dir,gs_remote_dir))
    if status !=0:
        logging.info([status,stdout])

# Execute script
def gs_android_init(ip):
    logging.info('{} run androdi_init.sh'.format(ip))
    for file_sh in gs_init_list:
        if file_sh == "game/Q8L_3288_100948_GAMES/18.MengHuanHuaYuan/ArchiveFile.sh":
            continue
        s, stdout=load_shell.shell('adb -s {}:5555 shell su -c sh {}'.format(ip,os.path.join(gs_remote_dir,file_sh)))
        print(file_sh)
        if s !=0:
            logging.info([s,stdout])

# Write region id
def set_region(ip):
    logging.info('{} set region'.format(ip))
    gsd_id= get_region.get_region() * 1000 + int(ip.split('.')[2]) * 100 + int(ip.split('.')[3])
    load_shell.shell('adb -s {}:5555 shell "echo {} >/sdcard/gsd_id.txt"'.format(ip, gsd_id))

# run GSD
def adb_start_gsd(ip):
    logging.info('{} adb start gsd'.format(ip))
    load_shell.shell('adb -s {}:5555 shell am start -n cn.gloud.gs_android_dog/cn.gloud.gs_android_dog.MainActivity'.format(ip))

# run main
def main():
    for ip in ip_list:
        try:
            try:
                lock.acquire()
                if ip in action_list:
                    continue
                else:
                    action_list.append(ip)
                    s = connect.connect(ip)
                    if s != 0:
                        logging.warning('{} not connect !!!'.format(ip))
                        continue

                    if connect.check(ip) != 0:
                        logging.warning('{} check err !!!'.format(ip))
                        continue
                    logging.info("{} start init".format(ip))
            finally:
                lock.release()

            setup_gs_android(ip)
            gs_android_init(ip)
            set_region(ip)
            
            connect.disconnect(ip)
            logging.info('{} ok!!!'.format(ip))
        except Exception as e:
            logging.warning([ip,e])
            continue

if __name__ == "__main__":
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1",44455))
    except Exception as e:
        logging.error(e)
        os._exit(1)
    for file_sh in gs_init_list:os.system('dos2unix {}'.format(os.path.join(gs_local_dir,file_sh)))

    thread_num=10

    lock=threading.Lock()
    thread_pool=[]
    for a in range(thread_num):
        t = threading.Thread(target=main,name='t{}'.format(a))
        t.start()
        thread_pool.append(t)
        time.sleep(2)
    for t in thread_pool:
        t.join()

logging.info('end!!')