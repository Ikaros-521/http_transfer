import logging, json
import webbrowser
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
# import asyncio
import os, sys
import traceback

from gradio_client import Client

from utils.common import Common
from utils.logger import Configure_logger
from utils.config import Config
from utils.LLM.chatgpt import Chatgpt
from utils.TTS.my_tts import MY_TTS

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

    port = 5900
    password = "中文的密码，怕了吧！"
    config_file_path = "config.json"

    app = Flask(__name__, static_folder='./')
    CORS(app)  # 允许跨域请求
    # socketio = SocketIO(app, cors_allowed_origins="*")

    # 全局数据
    config = Config(config_file_path)
    chatgpt = Chatgpt(config.get("openai"), config.get("chatgpt"))
    my_tts = MY_TTS(config_file_path)


    def self_reboot():
        try:
            # 获取当前 Python 解释器的可执行文件路径
            python_executable = sys.executable

            # 获取当前脚本的文件路径
            script_file = os.path.abspath(__file__)

            # 重启当前程序
            os.execv(python_executable, ['python', script_file])
        except Exception as e:
            print(f"Failed to restart the program: {e}")


    def check_password(data_json, ip):
        try:
            if data_json["password"] == password:
                return True
            else:
                return False
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error(f"[{ip}] 密码校验失败！{e}")
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

    # 设置一个路由来处理文件的访问
    @app.route('/out/<filename>')
    def uploaded_file(filename):
        return send_from_directory('out', filename)
    
    @app.route('/get_config', methods=['GET'])
    def get_config():
        try:
            
            # 打开文件并解析JSON数据
            with open(config_file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)

            return jsonify(data)
        except Exception as e:
            return jsonify({"code": -1, "message": f"获取本地配置失败{e}"})
        
    @app.route('/save_config', methods=['POST'])
    def save_config():
        try:
            content = request.get_json()
            logging.info(content)

            try:
                with open(config_file_path, 'w', encoding="utf-8") as config_file:
                    json.dump(content, config_file, indent=2, ensure_ascii=False)
                    config_file.flush()  # 刷新缓冲区，确保写入立即生效

                logging.info("配置数据已成功写入文件！")
                return jsonify({"code": 200, "message": "配置数据已成功写入文件！"})
            except Exception as e:
                logging.error(f"无法写入配置文件！{e}")
                return jsonify({"code": -1, "message": "无法写入配置文件！{e}"})

            
        except Exception as e:
            return jsonify({"code": -1, "message": f"无法写入配置文件！{e}"})

    """
    请求LLM获取返回的结果

    data_json = {
        "llm": "chatgpt",
        "prompt": "",
        "password": ""
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/get_llm_resp', methods=['POST'])
    def get_llm_resp():
        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json, request.remote_addr):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})

            resp_content = chatgpt.get_gpt_resp("主人", "你好")
            

            if resp_content:
                return jsonify({"code": 200, "message": "请求成功", "data": {"content": resp_content}})
            else:
                return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因"})
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因，{e}"})

    """
    请求TTS获取返回的结果

    data_json = {
        "tts": "bert-vits2",
        "content": "",
        "password": ""
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/get_tts_resp', methods=['POST'])
    async def get_tts_resp():
        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json, request.remote_addr):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})
            
            vits = config.get("vits")

            # 语言检测
            language = common.lang_check(data_json["content"])

            data = {
                "type": vits["type"],
                "api_ip_port": vits["api_ip_port"],
                "id": vits["id"],
                "format": vits["format"],
                "lang": language,
                "length": vits["length"],
                "noise": vits["noise"],
                "noisew": vits["noisew"],
                "max": vits["max"],
                "sdp_radio": vits["sdp_radio"],
                "content": data_json["content"]
            }
            
            resp_content = await my_tts.vits_api(data)
            logging.info(resp_content)

            if resp_content:
                return jsonify({"code": 200, "message": "请求成功", "data": {"file_path": resp_content}})
            else:
                return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因"})
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因，{e}"})

    """
    请求语音转视频获取返回的结果

    data_json = {
        "w2v": "sadtalker",
        "img_path": "",
        "audio_path": "",
        "password": ""
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/get_video_resp', methods=['POST'])
    async def get_video_resp():
        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json, request.remote_addr):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})
            
            
            client = Client("http://127.0.0.1:7860/")
            result = client.predict(
                data_json["img_path"],	# str (filepath or URL to image) in 'Source image' Image component
                data_json["audio_path"],	# str (filepath or URL to file) in 'Input audio' Audio component
                "crop",	# str  in 'preprocess' Radio component
                True,	# bool  in 'Still Mode (fewer hand motion, works with preprocess `full`)' Checkbox component
                True,	# bool  in 'GFPGAN as Face enhancer' Checkbox component
                2,	# int | float (numeric value between 0 and 10) in 'batch size in generation' Slider component
                256,	# str  in 'face model resolution' Radio component
                0,	# int | float (numeric value between 0 and 46) in 'Pose style' Slider component
                fn_index=0
            )
            logging.info(result)

            if result:
                result = common.move_file(result, os.path.join("./out", common.get_bj_time(7)), f"{common.get_bj_time(7)}")
                logging.info(result)
                return jsonify({"code": 200, "message": "请求成功", "data": {"file_path": f"out/{common.extract_filename(result)}"}})
            else:
                return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因"})
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因，{e}"})
        
    """
    重启程序

    data_json = {
        "password": ""
    }

    return:
        {"code": 200, "message": "成功"}
        {"code": -1, "message": "失败"}
    """
    @app.route('/reboot', methods=['POST'])
    async def reboot():
        try:
            data_json = request.get_json()
            logging.info(data_json)

            if not check_password(data_json, request.remote_addr):
                return jsonify({"code": -1, "message": f"[{request.remote_addr}] 请停止你的非法请求！"})

            self_reboot()

            return jsonify({"code": 200, "message": f"重启成功"})
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"code": -1, "message": f"请求失败，请查看日志，排查具体问题原因，{e}"})

    url = f'http://localhost:{port}/index.html'
    # webbrowser.open(url)
    logging.info(f"浏览器访问地址：{url}")
    app.run(host='0.0.0.0', port=port, debug=True)

