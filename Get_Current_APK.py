import os
import re
import winreg
from subprocess import Popen, PIPE

def get_desktop_path():
	key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
	return winreg.QueryValueEx(key,'Desktop')[0]


def get_output_path():
	desktop_path = get_desktop_path()
	output_path = input('请输入安装包保存地址 (默认 : '+desktop_path+'):')
	if output_path == '':
		output_path = desktop_path
	return output_path

def get_package_name():
	# 获得包名
	info=os.popen('adb shell dumpsys activity | findstr "mFocus"').read().split(" ")

	for i in info:
		if '/' in i and '.' in i :
			current_Package=i.split('/')[0]
	print('当前包名为:'+current_Package+"\n")
	return current_Package

def get_package_path_in_phone():
	return os.popen('adb shell pm path '+current_Package).read().split('package:')[1]

def pull_package_to_Computer(package_path, output_path):
	print("正在发送安装包到指定位置")
	os.system('adb pull '+package_path+' '+output_path)
def analyze_package_name(output_path):
	print("正在分析apk安装包的应用名")
	# 创建Pipe
	name = Popen('aapt dump badging '+output_path, shell=True, stdout = PIPE)
	# 读取Pipe
	name = name.stdout.read()
	# 把读取结果转换为字符串
	package_name=bytes.decode(name)
	name=re.search(r"application-label-zh-CN:'(.*?)'",package_name)
	if type(name ==None):
		name=re.search(r"application-label:'(.*?)'",package_name)
	apk_name=name.group(1).strip()
	print('apk名称为:'+apk_name+'\napk大小为:'+str(round(os.path.getsize(output_path)/1024/1024,2)))
	os.rename(output_path,os.path.join(os.path.dirname(output_path), apk_name)+'.apk')
	print('发送完成，保存为 '+os.path.join(os.path.dirname(output_path), apk_name)+".apk\n")
	return apk_name

output_path = get_output_path().strip()

current_Package=get_package_name()

full_output_path=os.path.join(output_path,current_Package+'.apk')

package_path = get_package_path_in_phone().strip()

pull_package_to_Computer(package_path, full_output_path)

analyze_package_name(full_output_path)
