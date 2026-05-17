# AoE4 Player Style Analyzer

本项目是一个本地 Windows 桌面 EXE 工具，用于快速查询《帝国时代 4》玩家战绩，并基于 AOE4 World API 的公开对局数据生成玩家风格和风险分析。

## 普通玩家怎么用

普通玩家可以只下载 `AoE4PlayerAnalyzer.exe`，双击运行即可，不需要安装 Python。

使用条件：

- Windows 系统
- 能联网访问 `aoe4world.com`
- 第一次启动可能会被 Windows Defender / SmartScreen 提醒，这是未签名个人 EXE 的常见情况


## 功能

- 搜索 AoE4 玩家
- 输入玩家名 3 个字符后自动联想匹配玩家；1-2 个字符可按回车或点击搜索进行精确匹配
- 按天梯单排、天梯组队、快速比赛模式分别统计
- 右侧中文输出玩家战绩、常用文明、地图、平均时长和风格画像
- 少于 3 分钟的对局不参与胜率、文明、地图、平均时长和打法统计
- 极短失败局仍会作为疑似炸鱼证据保留
- 检测疑似炸鱼、疑似高手小号、本地人/正常长期玩家
- 识别上分搭档候选和掉分搭档候选，同队至少 5 局才会判断为搭档
- 使用本地 SQLite 缓存，减少重复请求 AOE4 World API

## 声明

本项目是玩家自制、非商业工具，不隶属于 Microsoft、Relic Entertainment、World's Edge 或 AOE4 World。

分析结果基于 AOE4 World API 的公开对局数据和本项目内置规则生成。涉及“疑似炸鱼”“疑似小号”等表述时，均表示规则推断，不代表最终定性，也不能替代人工复盘。

## 从源码运行

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 打包 EXE

```powershell
.\.venv\Scripts\activate
pyinstaller --onefile --windowed --name AoE4PlayerAnalyzer app.py
```

生成文件在：

```text
dist\AoE4PlayerAnalyzer.exe
```

## API 使用说明

程序会通过 AOE4 World API 读取公开玩家和对局数据，并使用本地 SQLite 缓存减少重复请求。默认 User-Agent 为：

```text
AoE4PlayerAnalyzer/0.1 contact: github.com/galiceo/AOE4-Performance-Analysis
```

## License

This project is open source under the [MIT License](LICENSE).
