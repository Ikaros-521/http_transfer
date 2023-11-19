# 导入所需的库
import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import os
import requests
import json
import logging
import traceback
import langid
import re
import shutil

class Common:
    # 获取北京时间
    def get_bj_time(self, type=0):
        """获取北京时间

        Args:
            type (int, str): 返回时间类型. 默认为 0.
                0 返回数据：年-月-日 时:分:秒
                1 返回数据：年-月-日
                2 返回数据：当前时间的秒
                3 返回数据：自1970年1月1日以来的秒数
                4 返回数据：返回自1970年1月1日以来的毫秒数 % 100
                5 返回数据：当前 时点分
                6 返回数据：当前时间的 时, 分
                7 返回数据：年-月-日-时:分:秒

        Returns:
            str: 返回指定格式的时间字符串
            int, int
        """
        if type == 0:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d %H:%M:%S'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt
        elif type == 1:
            now = datetime.now()  # 获取当前时间
            year = now.year  # 获取当前年份
            month = now.month  # 获取当前月份
            day = now.day  # 获取当前日期

            return str(year) + "-" + str(month) + "-" + str(day)
        elif type == 2:
            now = time.localtime()  # 获取当前时间

            # hour = now.tm_hour   # 获取当前小时
            # minute = now.tm_min  # 获取当前分钟 
            second = now.tm_sec  # 获取当前秒数

            return str(second)
        elif type == 3:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数

            return str(current_time)
        elif type == 4:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数
            current_milliseconds = int(current_time * 1000) # 毫秒为单位
            tgt_time = current_milliseconds % 100 # 用于生成音频文件名

            return str(tgt_time)
        elif type == 5:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟

            return str(hour) + "点" + str(minute) + "分"
        elif type == 6:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟 

            return hour, minute
        elif type == 7:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d-%H-%M-%S'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt

    # 语言检测 TODO:有内存泄漏风险
    def lang_check(self, text, need="none"):
        # 语言检测 一个是语言，一个是概率
        language, score = langid.classify(text)

        if need == "none":
            return language
        else:
            if language != need:
                return None
            else:
                return language

    # 文本切分算法
    def split_sentences(self, text):
        # 使用正则表达式切分句子
        sentences = re.split(r'(?<=[。！？!?])', text)
        result = []
        current_sentence = ""
        
        for sentence in sentences:
            # 去除换行和空格
            sentence = sentence.replace('\n', '')
            
            # 如果句子为空则跳过
            if not sentence:
                continue
            
            # 如果句子长度小于10个字，则与下一句合并
            if len(current_sentence) < 10:
                current_sentence += sentence
            else:
                # 判断当前句子是否以标点符号结尾
                if current_sentence[-1] in ["。", "！", "？", ".", "!", "?"]:
                    result.append(current_sentence)
                    current_sentence = sentence
                else:
                    # 如果当前句子不以标点符号结尾，则进行二次切分
                    split_sentences = re.split(r'(?<=[,，;；])', current_sentence)
                    if len(split_sentences) > 1:
                        result.extend(split_sentences[:-1])
                        current_sentence = split_sentences[-1] + sentence
                    else:
                        current_sentence += sentence
        
        # 添加最后一句
        if current_sentence:
            result.append(current_sentence)
        
        return result

    """
    音频相关
    """
    # 获取新的音频路径
    def get_new_audio_path(self, audio_out_path, file_name):
        # 判断路径是否为绝对路径
        if os.path.isabs(audio_out_path):
            # 如果是绝对路径，直接使用
            voice_tmp_path = os.path.join(audio_out_path, file_name)
        else:
            # 如果不是绝对路径，检查是否包含 ./，如果不包含，添加 ./，然后拼接路径
            if not audio_out_path.startswith('./'):
                audio_out_path = './' + audio_out_path
            voice_tmp_path = os.path.normpath(os.path.join(audio_out_path, file_name))

        voice_tmp_path = os.path.abspath(voice_tmp_path)

        return voice_tmp_path


    """
    视频相关
    """
    # 移动文件到指定路径 src dest
    def move_file(self, source_path, destination_path, rename=None, format="mp4"):
        """移动文件到指定路径

        Args:
            source_path (str): 文件路径含文件名
            destination_path (_type_): 目标文件夹
            rename (str, optional): 文件名. Defaults to None.
            format (str, optional): 文件格式（实际上只是个假拓展名）. Defaults to "mp4".

        Returns:
            str: 输出到的完整路径含文件名
        """
        logging.debug(f"source_path={source_path},destination_path={destination_path},rename={rename}")

        # if os.path.exists(destination_path):
        #     # 如果目标位置已存在同名文件，则先将其移动到回收站
        #     send2trash(destination_path)
        
        # if rename is not None:
        #     destination_path = os.path.join(os.path.dirname(destination_path), rename)
        
        # shutil.move(source_path, destination_path)
        # logging.info(f"文件移动成功：{source_path} -> {destination_path}")
        destination_directory = os.path.dirname(destination_path)
        logging.debug(f"destination_directory={destination_directory}")
        destination_filename = os.path.basename(source_path)

        if rename is not None:
            destination_filename = rename + "." + format
        
        destination_path = os.path.join(destination_directory, destination_filename)
        
        if os.path.exists(destination_path):
            # 如果目标位置已存在同名文件，则先删除
            os.remove(destination_path)

        shutil.move(source_path, destination_path)
        print(f"文件移动成功：{source_path} -> {destination_path}")

        return destination_path
    
    # 从文件路径中提取出带有扩展名的文件名
    def extract_filename(self, file_path, with_extension=True):
        """从文件路径中提取出带有扩展名的文件名

        Args:
            file_path (_type_): 文件路径
            with_extension (bool, optional): 是否需要拓展名. Defaults to True.

        Returns:
            str: 文件名
        """
        file_name_with_extension = os.path.basename(file_path)
        if with_extension:
            return file_name_with_extension
        else:
            file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
            return file_name_without_extension
        