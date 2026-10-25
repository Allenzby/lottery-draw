# 摇号软件 lottery-draw

一个简单的 Windows 摇号（随机抽号）程序：配置好抽取范围，输入要抽几个，点击「开始摇号」即可。

![界面](docs/screenshot.png)

## 功能

- 抽取范围写在 `config.json` 里，界面自动显示「抽取范围：1 ~ 100（共 100 个数字）」
- 输入摇号数量，点击**开始摇号**，数字滚动约 1.5 秒后**一次性揭晓**
- 结果**不重复**（在范围内不放回抽样）
- 数量超出范围会弹窗提示，窗口按结果数量自动放大
- 自带图标：exe 文件图标 + 窗口标题栏图标

## 使用

1. 下载 [Releases](../../releases) 里的 `摇号软件.exe`
2. 旁边放一个 `config.json`（首次运行会自动生成默认配置）
3. 双击 exe，输入数量，点「开始摇号」

## 配置文件 config.json

```json
{
    "title": "摇号软件",   // 窗口标题
    "min": 1,             // 抽取范围起始
    "max": 100,           // 抽取范围结束
    "default_count": 5,   // 数量输入框默认值
    "animation_ms": 1500, // 滚动动画时长（毫秒）
    "interval_ms": 60     // 滚动刷新间隔（毫秒）
}
```

改完保存，重新打开 exe 即生效；删掉配置文件程序会自动生成默认的。

> 注意：`config.json` 请用 UTF-8 编码保存。

## 开发

直接运行源码：

```powershell
python app.py
```

### 打包成 exe

```powershell
pip install pyinstaller
python -m PyInstaller -F -w --clean -n "摇号软件" --icon icon.ico app.py
copy dist\摇号软件.exe .
```

### 修改图标

图标由 `make_icon.py` 用 Pillow 生成（16/24/32/48/64/128/256 全尺寸），并会把窗口图标数据自动注入 `app.py`：

```powershell
pip install pillow
python make_icon.py
# 然后按上面的命令重新打包
```

## 项目结构

```
app.py          主程序（Tkinter 界面 + 摇号逻辑）
config.json     配置文件（范围、标题、动画参数）
icon.ico        多尺寸图标（打包用）
icon.png        64px 图标源图
make_icon.py    图标生成脚本
```

## License

MIT
