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
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/e26dae85-eec8-458f-8cea-1bdd8664c8d8)


### 获取数据
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/fb89f528-894d-452c-adc3-9e9dee9dab77)


### 删除数据
![image](https://github.com/Ikaros-521/http_transfer/assets/40910637/ad55912a-8073-427b-afd1-68e68a94538b)



# FAQ

1.5700端口冲突  
可以修改`app.py`和`js/index.js`中，搜索`5700`，全部改成你的新端口即可。  

# 更新日志

- 2023-11-17
  - 增加密码传参校验
  - 补充IP地址输出

- 2023-11-12
  - 初版demo发布
  - 补充运行脚本（请将Miniconda3安装在项目文件夹，并命名为Miniconda3，才能正常使用，要么自行适配）
