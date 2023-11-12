# 前言
HTTP中转站，用于2个http客户端的数据传输中转。  

# 使用&部署
开发系统：win11  
python：3.10  
安装依赖：`pip install -r requirements.txt`  
运行：`python app.py`  
浏览器访问：`http://127.0.0.1:5700/index.html`  

## 整合包

github：[https://github.com/Ikaros-521/http_transfer/releases](https://github.com/Ikaros-521/http_transfer/releases)  

## API


# FAQ

1.5700端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5700`，全部改成你的新端口即可。  

# 更新日志

- 2023-11-12
  - 初版demo发布