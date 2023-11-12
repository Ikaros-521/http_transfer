const server_port = 5700;
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

function showtip(type, text, timeout=3000) {
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
 

