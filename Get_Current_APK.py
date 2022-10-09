import os
import re
import winreg
from subprocess import Popen, PIPE

def get_desktop_path():
	# 获取桌面地址
	key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
	return winreg.QueryValueEx(key,'Desktop')[0]


def get_output_path():
	# 获取输出提取的安装包的地址
	desktop_path = get_desktop_path()
	output_path = input('请输入安装包保存地址 (默认 : '+desktop_path+'):')
	if output_path == '':
		output_path = desktop_path
	return output_path

def get_package_name():
	# 获得前台正在运行的应用的包名
	info=os.popen('adb shell dumpsys activity | findstr "mFocus"').read().split(" ")
	
	current_Package =''
	for i in info:
		if '/' in i and '.' in i :
			current_Package=i.split('/')[0]
	if current_Package =='':
		info = os.popen("adb shell dumpsys window | findstr mCurrentFocus ").read().split(" ")
	for i in info:
		if '/' in i and '.' in i :
			current_Package=i.split('/')[0]
	if current_Package =='':
		current_Package='空'
	print('当前包名为:'+current_Package+"\n")
	return current_Package

def get_package_path_in_phone():
	# 通过Activity获取包在手机中的地址
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

def main():
	global current_Package 
	output_path = get_output_path().strip() # 获取输出提取的安装包的地址

	current_Package=get_package_name() # 获取需要提取的安装包的包名

	full_output_path=os.path.join(output_path,current_Package+'.apk') # 拼接出完整的输出地址

	package_path = get_package_path_in_phone().strip() # 拼接需要提取的安装包的包名

	pull_package_to_Computer(package_path, full_output_path) # 输出安装包到电脑

	analyze_package_name(full_output_path) # 分析安装包的应用名称
main()