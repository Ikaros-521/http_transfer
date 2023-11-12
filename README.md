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

### 添加数据
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/b7d5ba45-2f92-4aad-bb5c-10914ee02767)

### 获取数据
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/7375a398-fa5a-4520-a491-ba44ffbb40c3)

### 删除数据
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/49f33fa8-9253-4154-9fb4-4558e29a32c4)


# FAQ

1.5700端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5700`，全部改成你的新端口即可。  

# 更新日志

- 2023-11-12
  - 初版demo发布
  - 补充运行脚本（请将Miniconda3安装在项目文件夹，并命名为Miniconda3，才能正常使用，要么自行适配）
