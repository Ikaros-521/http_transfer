const server_port = 5900;
let config = null;
let tipCounter = 0;

/***
 * 通用工具
***/
// 获取输入框中的值并转为整数
function getNumber(input, defaultValue = 0) {
    let value = input.value;
    let number = parseInt(value);

    if (isNaN(number) || value === '') {
        number = defaultValue;
    }

    return number;
}

function showtip(type, text, timeout = 3000) {
    const tip = document.createElement("div");
    tip.className = "tip";
    tip.style.bottom = `${tipCounter * 40}px`; // 垂直定位
    tip.innerText = text;
    if (type == "error") {
        tip.style.backgroundColor = "#ff0000";
    }

    document.body.appendChild(tip);

    setTimeout(function () {
        document.body.removeChild(tip);
        tipCounter--;
    }, timeout);

    tipCounter++;
}

function changeVideoSource(file_path) {
    var videoElement = document.getElementById('my_video');
    var sourceElement = document.getElementById('my_video_source');

    // Set the new video source
    sourceElement.src = file_path;

    // You might need to explicitly tell the browser to reload the video element
    videoElement.load();
}

function showPage(pageId) {
    // Hide all pages
    var pages = document.getElementsByClassName('page');
    for (var i = 0; i < pages.length; i++) {
        pages[i].classList.remove('active');
    }

    // Show the selected page
    var selectedPage = document.getElementById(pageId);
    selectedPage.classList.add('active');
}


function init_config() {
    // JavaScript code to populate the select options
    var chatgptModels = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-4-1106-preview",
        "text-embedding-ada-002",
        "text-davinci-003",
        "text-davinci-002",
        "text-curie-001",
        "text-babbage-001",
        "text-ada-001",
        "text-moderation-latest",
        "text-moderation-stable",
        "rwkv",
        "chatglm3-6b"
    ];

    var selectElement = document.getElementById('select_chatgpt_model');

    chatgptModels.forEach(function(model) {
        var option = document.createElement('option');
        option.value = model;
        option.text = model;
        selectElement.appendChild(option);
    });

    document.getElementById('input_openai_api').value = config["openai"]["api"];
    document.getElementById('input_openai_api_key').value = config["openai"]["api_key"];
    document.getElementById('select_chatgpt_model').value = config["openai"]["model"];

    document.getElementById('input_chatgpt_temperature').value = config["chatgpt"]["temperature"];
    document.getElementById('input_chatgpt_max_tokens').value = config["chatgpt"]["max_tokens"];
    document.getElementById('input_chatgpt_top_p').value = config["chatgpt"]["top_p"];
    document.getElementById('input_chatgpt_presence_penalty').value = config["chatgpt"]["presence_penalty"];
    document.getElementById('input_chatgpt_frequency_penalty').value = config["chatgpt"]["frequency_penalty"];
    document.getElementById('input_chatgpt_preset').value = config["chatgpt"]["preset"];

    document.getElementById('select_vits_type').value = config["vits"]["type"];
    document.getElementById('input_vits_config_path').value = config["vits"]["config_path"];
    document.getElementById('input_vits_api_ip_port').value = config["vits"]["api_ip_port"];
    document.getElementById('input_vits_id').value = config["vits"]["id"];
    document.getElementById('select_vits_lang').value = config["vits"]["lang"];
    document.getElementById('input_vits_length').value = config["vits"]["length"];
    document.getElementById('input_vits_noise').value = config["vits"]["noise"];
    document.getElementById('input_vits_noisew').value = config["vits"]["noisew"];
    document.getElementById('input_vits_max').value = config["vits"]["max"];
    document.getElementById('input_vits_format').value = config["vits"]["format"];
    document.getElementById('input_vits_sdp_radio').value = config["vits"]["sdp_radio"];
}

/***
 * 网络请求
***/

// 封装 HTTP 请求接口
function commonHttpRequest(url, method, data) {
    return new Promise((resolve, reject) => {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                // 可根据需要添加其他头部信息，比如 API key
            },
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                resolve(data);
            })
            .catch(error => {
                reject(error);
            });
    });
}

// 获取当前配置
function get_config() {
    var url = `http://127.0.0.1:${server_port}/get_config`;

    commonHttpRequest(url, "GET")
        .then(response => {
            console.log('get_config Response:', response);
            showtip("info", '获取本地配置成功');
            config = response;
            init_config();
        })
        .catch(error => {
            console.error('get_config Error:', error);
            showtip("error", 'get_config Error:' + error.toString());
        });
}

get_config();

// 保存配置
function save_config() {
    try {
        config["openai"]["api"] = document.getElementById('input_openai_api').value;
        config["openai"]["api_key"] = document.getElementById('input_openai_api_key').value;
        config["openai"]["model"] = document.getElementById('select_chatgpt_model').value;

        config["chatgpt"]["temperature"] = parseFloat(document.getElementById('input_chatgpt_temperature').value).toFixed(1);
        config["chatgpt"]["max_tokens"] = parseInt(document.getElementById('input_chatgpt_max_tokens').value);
        config["chatgpt"]["top_p"] = parseFloat(document.getElementById('input_chatgpt_top_p').value).toFixed(1);
        config["chatgpt"]["presence_penalty"] = parseFloat(document.getElementById('input_chatgpt_presence_penalty').value).toFixed(1);
        config["chatgpt"]["frequency_penalty"] = parseFloat(document.getElementById('input_chatgpt_frequency_penalty').value).toFixed(1);
        config["chatgpt"]["preset"] = document.getElementById('input_chatgpt_preset').value;

        config["vits"]["type"] = document.getElementById('select_vits_type').value;
        config["vits"]["config_path"] = document.getElementById('input_vits_config_path').value;
        config["vits"]["api_ip_port"] = document.getElementById('input_vits_api_ip_port').value;
        config["vits"]["id"] = document.getElementById('input_vits_id').value;
        config["vits"]["lang"] = document.getElementById('select_vits_lang').value;
        config["vits"]["length"] = document.getElementById('input_vits_length').value;
        config["vits"]["noise"] = document.getElementById('input_vits_noise').value;
        config["vits"]["noisew"] = document.getElementById('input_vits_noisew').value;
        config["vits"]["max"] = document.getElementById('input_vits_max').value;
        config["vits"]["format"] = document.getElementById('input_vits_format').value;
        config["vits"]["sdp_radio"] = document.getElementById('input_vits_sdp_radio').value;

    } catch (error) {
        console.error(error);
        showtip("error", "保存配置失败，" + error.toString());
        return;
    }

    const url = `http://127.0.0.1:${server_port}/save_config`;

    commonHttpRequest(url, "POST", config)
        .then(response => {
            console.log('save_config Response:', response);
            showtip("info", "保存配置成功");
        })
        .catch(error => {
            console.error('save_config Error:', error);
            showtip("error", "保存配置失败，" + error.toString());
        });

}

function send_prompt_to_llm() {
    let data_json = {
        "llm": "chatgpt",
        "prompt": document.getElementById("input_prompt").value,
        "password": "中文的密码，怕了吧！"
    };

    commonHttpRequest(`http://127.0.0.1:${server_port}/get_llm_resp`, "POST", data_json)
        .then(response => {
            console.log('send_prompt_to_llm Response:', response);
            showtip("info", '获取LLM结果成功');
            document.getElementById("textarea_llm_resp").value = response["data"]["content"];
        })
        .catch(error => {
            console.error('send_prompt_to_llm Error:', error);
            showtip("error", 'send_prompt_to_llm Error:' + error.toString());
        });
}

function send_content_to_tts() {
    let data_json = {
        "tts": "bert-vits2",
        "content": document.getElementById("textarea_llm_resp").value,
        "password": "中文的密码，怕了吧！"
    };

    commonHttpRequest(`http://127.0.0.1:${server_port}/get_tts_resp`, "POST", data_json)
        .then(response => {
            console.log('send_content_to_tts Response:', response);
            showtip("info", '合成音频成功');
            send_content_to_w2v(response["data"]["file_path"]);
        })
        .catch(error => {
            console.error('send_content_to_tts Error:', error);
            showtip("error", 'send_content_to_tts Error:' + error.toString());
        });
}

function send_content_to_w2v(audio_path) {
    let data_json = {
        "w2v": "sadtalker",
        "img_path": "E:\\AI-Video-Generator\\data\\1.png",
        "audio_path": audio_path,
        "password": "中文的密码，怕了吧！"
    };

    showtip("info", '即将合成视频，请耐心等待...');

    commonHttpRequest(`http://127.0.0.1:${server_port}/get_video_resp`, "POST", data_json)
        .then(response => {
            console.log('send_content_to_w2v Response:', response);
            showtip("info", '合成视频成功');
            changeVideoSource(response["data"]["file_path"]);
        })
        .catch(error => {
            console.error('send_content_to_w2v Error:', error);
            showtip("error", 'send_content_to_w2v Error:' + error.toString());
        });
}
