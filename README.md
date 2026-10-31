# 摇号软件 lottery-draw

一个简单的摇号（随机抽号）程序：配置好抽取范围，输入要抽几个，点击「开始摇号」即可。
**Windows（exe）和安卓（apk）双平台**，界面和规则一致。

![Windows 界面](docs/screenshot.png)

## 下载

| 平台 | 文件 | 说明 |
|---|---|---|
| Windows | [Releases](../../releases) 里的 `摇号软件.exe` | 双击运行，旁边放 `config.json` |
| Android | [Releases](../../releases) 里的 `摇号软件.apk` | 手机上安装，需允许「安装未知来源应用」 |

> 发布页显示中文名，实际下载文件名是 `lottery-draw-v1.1.exe` / `lottery-draw-v1.1.apk`，可以自行改名。

## 功能

- 抽取范围写在配置里，界面显示「抽取范围：1 ~ 100（共 100 个数字）」
- 输入摇号数量，点击**开始摇号**，数字滚动约 1 秒后**一次性揭晓**
- 结果**不重复**（在范围内不放回抽样）
- 数量超出范围会提示，窗口/页面按结果数量自动调整
- 自带图标：exe 文件图标、窗口标题栏图标、安卓启动图标

## Windows 版

1. 下载 exe，旁边放一个 `config.json`（首次运行会自动生成默认配置）
2. 双击 exe，输入数量，点「开始摇号」

配置文件 `config.json`：

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

> 请用 UTF-8 编码保存；删掉配置文件程序会自动生成默认的。

## 安卓版

- 安装后打开即可用，点右上角 **⚙ 设置** 可以改抽取范围（起始、结束、默认数量），保存在本机
- 默认值来自 `android/assets/config.js`（打包时写进 APK）：

```js
window.APP_CONFIG = {
    "title": "摇号软件",
    "min": 1,
    "max": 50,
    "default_count": 1,
    "animation_ms": 1200,
    "interval_ms": 60
};
```

- 支持 Android 5.0（API 21）及以上

## 开发

### Windows 源码

```powershell
python app.py
```

打包成 exe：

```powershell
pip install pyinstaller
python -m PyInstaller -F -w --clean -n "摇号软件" --icon icon.ico app.py
copy dist\摇号软件.exe .
```

### 安卓 APK

不需要 Android Studio / Gradle，用 JDK + Android build-tools 手工构建：

```powershell
# 依赖：JDK 17+、build-tools 34、platform(android.jar)
powershell -ExecutionPolicy Bypass -File android\build.ps1
# 指定版本：-Version 1.2 -VersionCode 3
```

脚本会依次执行 aapt2 编译/链接资源 → javac → d8 → 打包 dex → zipalign → apksigner 签名，
产物为项目根目录的 `摇号软件-v1.1.apk`。

> 注意：
> - `aapt2` 不支持中文路径，脚本会先把工程复制到 `%TEMP%\lottery-android` 再构建
> - 首次构建会生成签名密钥 `android/lottery-release.jks`（默认密码 `lotterydraw`）。
>   **请备份这个文件**，以后升级必须用同一个密钥签名，否则无法覆盖安装

### 修改图标

图标由 `make_icon.py` 用 Pillow 生成（Windows 全尺寸 ico + 安卓 5 个密度），
并把窗口图标数据自动注入 `app.py`：

```powershell
pip install pillow
python make_icon.py
# 然后重新打包 exe / apk
```

## 项目结构

```
app.py                    Windows 主程序（Tkinter）
config.json               Windows 配置
icon.ico / icon.png       图标源文件
make_icon.py              图标生成脚本（含安卓图标）
docs/screenshot.png       界面截图
android/
  AndroidManifest.xml     应用清单（包名、版本、权限）
  java/.../MainActivity.java   WebView 壳
  assets/index.html       安卓界面与摇号逻辑（HTML/CSS/JS）
  assets/config.js        安卓默认配置
  res/                    应用名、启动图标
  build.ps1               一键构建 APK
```

## License

MIT
