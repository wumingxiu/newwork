#coding=utf-8
import os

from copy import copy

print("请输入你想复制的文件夹路径")
copy_dir=raw_input("copy_dir:")
print("请输入你想粘贴的文件夹路径")
paste_dir=raw_input("paste_dir:")

# copy_dir_list=os.listdir(copy_dir)
# for file in copy_dir_list:
#     print os.system("copy %s %s"%(file,paste_dir))

print os.system("xcopy %s %s"%(copy_dir,paste_dir))