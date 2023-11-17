import logging, json
import webbrowser
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
# import asyncio
import os, sys

from utils.common import Common
from utils.logger import Configure_logger

common = Common()

# 日志文件路径
log_file = "./log/log-" + common.get_bj_time(1) + ".txt"
Configure_logger(log_file)

# 获取 werkzeug 库的日志记录器
werkzeug_logger = logging.getLogger("werkzeug")
# 设置 httpx 日志记录器的级别为 WARNING
werkzeug_logger.setLevel(logging.WARNING)


if __name__ == '__main__':
    os.environ['GEVENT_SUPPORT'] = 'True'

    port = 5700
    password = "中文的密码，怕了吧！"

    app = Flask(__name__, static_folder='./')
    CORS(app)  # 允许跨域请求
    socketio = SocketIO(app, cors_allowed_origins="*")

    # 全局数据
    global_data_list = []

    def self_restart():
        try:
            # 获取当前 Python 解释器的可执行文件路径
            python_executable = sys.executable

            # 获取当前脚本的文件路径
            script_file = os.path.abspath(__file__)

            # 重启当前程序
            os.execv(python_executable, ['python', script_file])
        except Exception as e:
            print(f"Failed to restart the program: {e}")


    def check_password(data_json):
        try:
            if data_json["password"] == password:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"密码校验失败！{e}")
            return False


    @app.route('/index.html')
    def serve_file():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/css/index.css')
    def serve_file2():
        return send_from_directory(app.static_folder, 'css/index.css')

    @app.route('/js/index.js')
    def serve_file3():
        return send_from_directory(app.static_folder, 'js/index.js')

    """
    删除list数据

    data_json = {
        "start_index": 0,
        "end_index": 2,
        "all": true
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/clear', methods=['POST'])
    def clear():
        global global_data_list

        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})

            if data_json["all"]:
                global_data_list = []
            else:
                if 0 == len(global_data_list):
                    return jsonify({"code": 200, "message": f"数据列表为空，无需清空"})
                # 确保起始索引不越界
                if data_json["start_index"] >= len(global_data_list):
                    return jsonify({"code": -2, "message": f"起始索引越界"})

                # 确保起始索引不越界
                if data_json["start_index"] < 0:
                    data_json["start_index"] = 0

                # 确保结束索引不越界，如果超出列表长度，设置为列表末尾
                if data_json["end_index"] >= len(global_data_list):
                    data_json["end_index"] = len(global_data_list) - 1
                
                # 从列表中删除指定范围内的内容
                del global_data_list[data_json["start_index"]:data_json["end_index"]+1]

            return jsonify({"code": 200, "message": "删除数据成功！"})
        except Exception as e:
            return jsonify({"code": -1, "message": f"删除数据失败！{e}"})

    """
    获取list数据

    data_json = {
        "start_index": 0,
        "end_index": 2,
        "delete": true
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/get_list', methods=['POST'])
    def get_list():
        global global_data_list

        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})

            if 0 == len(global_data_list):
                return jsonify({"code": -3, "message": f"数据列表为空"})
            # 确保起始索引不越界
            if data_json["start_index"] >= len(global_data_list):
                return jsonify({"code": -2, "message": f"起始索引越界"})

            # 确保起始索引不越界
            if data_json["start_index"] < 0:
                data_json["start_index"] = 0

            # 确保结束索引不越界，如果超出列表长度，设置为列表末尾
            if data_json["end_index"] >= len(global_data_list):
                data_json["end_index"] = len(global_data_list) - 1
                
            # 获取指定范围内的内容
            selected_items = global_data_list[data_json["start_index"]:data_json["end_index"]+1]

            if data_json["delete"]:
                # 从列表中删除指定范围内的内容
                del global_data_list[data_json["start_index"]:data_json["end_index"]+1]

            return jsonify({"code": 200, "message": "获取数据成功", "data": selected_items})
        except Exception as e:
            return jsonify({"code": -1, "message": f"获取数据失败！{e}"})

    """
    添加数据到list

    data_json = {
        ...
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/add', methods=['POST'])
    def add():
        global global_data_list

        try:
            try:
                data_json = request.get_json()
                logging.info(data_json)

                if not check_password(data_json):
                    return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})

                global_data_list.append(data_json)

                logging.info("添加数据成功！")
                return jsonify({"code": 200, "message": "添加数据成功！"})
            except Exception as e:
                logging.error(f"添加数据失败！{e}")
                return jsonify({"code": -1, "message": f"添加数据失败！{e}"})

        except Exception as e:
            return jsonify({"code": -1, "message": f"添加数据失败！{e}"})


    url = f'http://localhost:{port}/index.html'
    # webbrowser.open(url)
    # logging.info(f"浏览器访问地址：{url}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
