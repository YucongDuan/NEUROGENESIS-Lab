# NEUROGENESIS Lab 中文入口

[在线项目页](https://yucongduan.github.io/NEUROGENESIS-Lab/) · [完整版本下载](https://github.com/YucongDuan/NEUROGENESIS-Lab/releases/tag/v1.0.0) · [English](README.md)

从神经机制到可修订证据。本系统提供 24 个注册神经机制实验、18 章导读、证据记忆与可重放实验记录。

在线页面可直接阅读随附的合成实验报告。需要修改参数、重新计算或操作完整界面时，请下载并解压 ZIP，在项目目录中使用 Python 3.10 及以上版本运行：

```bash
python run.py list
python run.py run hh --out runs/my-hh
python run.py replay runs/my-hh
python run.py serve --port 8766
```

启动服务器后打开 `http://127.0.0.1:8766`；关闭时按 Ctrl+C。源码运行不需要安装第三方运行时依赖、API 密钥或下载模型。

本次发布运行了 235 项本地测试并全部通过。25 份实验记录已重新计算，数值结果一致。 持续集成的实际平台和提交结果请查看 [GitHub Actions](https://github.com/YucongDuan/NEUROGENESIS-Lab/actions)。

[英文手册](docs/NEUROGENESIS_Lab_English_Handbook.docx) · [运行指南](GETTING_STARTED.md) · [发布记录](PUBLICATION_2026-09-28.md) · [全部项目](https://github.com/YucongDuan/YucongDuan/blob/main/REPOSITORY_DIRECTORY.zh-CN.md)

原始代码和文档许可为 Apache-2.0，保留原作者及贡献者署名。模型用于研究与教学，合成实验结果不构成临床效果、完整大脑模拟或主观体验的证明。
