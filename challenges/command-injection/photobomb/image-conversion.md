---
summary: 检查照片打印服务如何把转换选项传递给图像处理程序。
level: medium
lab: photobomb
---

# 场景

照片打印服务允许用户选择图片格式和尺寸。普通请求能够正常返回转换后的图片，但服务还需要把用户提交的选项交给服务器端的图像处理程序。

请检查应用如何构造并执行转换操作。

# 任务

通过正常的照片转换功能验证输入是否能够影响服务器端命令执行，取得应用运行账户的权限并提交 Flag。

~~~quiz
title: Image Conversion
kind: flag
prompt: |
  调查图片转换请求与服务器端处理程序之间的关系，取得应用运行账户的权限并提交 User Flag。
answer: "TTP{photobomb_user_default}"
match: trim
hint: 对比正常格式值与服务端实际执行的转换命令。
~~~
