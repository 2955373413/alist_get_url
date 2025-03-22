# Alist 文件列表获取工具

[![Gitee stars](https://gitee.com/webplan/alistfs/badge/star.svg?theme=dark)](https://gitee.com/webplan/alistfs)
[![Gitee forks](https://gitee.com/webplan/alistfs/badge/fork.svg?theme=dark)](https://gitee.com/webplan/alistfs)

这是一个用于获取 Alist 网盘文件列表的 Python 工具。支持递归获取目录结构、文件下载链接，并可以将结果保存为 JSON 格式。

## 功能特点

- 支持递归获取目录结构
- 显示文件大小和类型图标
- 获取文件下载链接
- 支持带空格的文件路径
- 自动处理密码保护的目录
- 结果可以保存为 JSON 格式

## 环境配置

### 方法一：使用 environment.yml

```bash
# 创建环境
conda env create -f environment.yml --prefix ./.env

# 激活环境
conda activate ./.env
```

### 方法二：手动创建

```bash
# 创建环境
conda create --prefix ./.env python=3.9

# 激活环境
conda activate ./.env

# 安装依赖
pip install requests
```

## 安装

```bash
# 克隆仓库
git clone https://gitee.com/webplan/alistfs.git

# 进入目录
cd alist_crawler

# 创建并激活环境
conda env create -f environment.yml --prefix ./.env
conda activate ./.env
```

## 使用方法

1. 激活环境：
```bash
conda activate ./.env
```

2. 运行脚本：
```bash
python alist_crawler.py
```

3. 查看结果：
- 控制台会显示文件列表
- `files_info.json` 包含详细信息

## 配置说明

在 `alist_crawler.py` 中可以修改以下参数：

```python
def main():
    alist_url = "https://pan.xiaolibai.cn"  # Alist 网站地址
    client = AlistClient(
        alist_url,
        max_retries=5,    # 最大重试次数
        retry_delay=1.0   # 重试延迟（秒）
    )
    max_depth = 2         # 最大递归深度
```

## 输出示例

### 控制台输出
```
📂 路径: /文档
------------------------------
📁 工作文件
📄 测试文档.pdf (2.5MB)
  🔗 URL: https://...
🎬 教学视频.mp4 (156.7MB)
  🔗 URL: https://...
```

### JSON 输出
```json
{
  "name": "测试文档.pdf",
  "path": "/文档/测试文档.pdf",
  "encoded_path": "/文档/测试文档.pdf",
  "type": "pdf",
  "icon": "📄",
  "size": 2621440,
  "size_formatted": "2.50MB",
  "modified": "2024-03-20 10:00:00",
  "url": "https://...",
  "accessible": true
}
```

## 文件类型图标

支持以下文件类型的图标显示：

- 视频文件 (🎬): mp4, mkv, avi, mov
- 音频文件 (🎵): mp3, wav, flac
- 图片文件 (🖼️): jpg, jpeg, png, gif, webp
- 文档文件 (📄,📝,📊): pdf, doc, docx, xls, xlsx, txt
- 压缩文件 (📦): zip, rar, tar, 7z, gz
- 代码文件 (🐍,☕,📜): py, java, js, html, css, json
- 系统文件 (⚙️,💿): exe, msi, dmg, iso, img

## 常见问题

1. 目录访问失败
   - 检查目录是否需要密码
   - 增加重试次数和延迟时间
   - 检查网络连接

2. 带空格的路径问题
   - 脚本会自动处理空格，无需手动编码

3. 中文路径问题
   - 支持中文路径，无需特殊处理

## 开发文档

### 主要类和方法

#### AlistClient 类

```python
class AlistClient:
    def __init__(self, base_url: str, max_retries: int = 5, retry_delay: float = 1.0):
        """
        初始化 AlistClient
        
        Args:
            base_url: Alist 网站地址
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """

    def get_file_list(self, path: str = '/') -> Optional[Dict]:
        """
        获取指定路径下的文件列表
        
        Args:
            path: 目录路径
            
        Returns:
            文件列表信息字典
        """

    def get_file_url(self, path: str) -> Optional[str]:
        """
        获取文件下载链接
        
        Args:
            path: 文件路径
            
        Returns:
            文件下载链接
        """
```

### 扩展开发

1. 添加新的文件类型：
```python
self.file_icons = {
    'new_type': '🆕',  # 添加新的文件类型图标
    # ...
}
```

2. 自定义输出格式：
修改 `print_file_list` 或 `get_all_files_info`