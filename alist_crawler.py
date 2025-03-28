import requests
import json
import time
import os
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

class AlistClient:
    def __init__(self, base_url: str, max_retries: int = 5, retry_delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 文件类型图标映射
        self.file_icons = {
            # 视频文件
            'video': '🎬',
            'mp4': '🎬',
            'mkv': '🎬',
            'avi': '🎬',
            'mov': '🎬',
            
            # 音频文件
            'audio': '🎵',
            'mp3': '🎵',
            'wav': '🎵',
            'flac': '🎵',
            
            # 图片文件
            'image': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'webp': '🖼️',
            
            # 文档文件
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'xls': '📊',
            'xlsx': '📊',
            'ppt': '📽️',
            'pptx': '📽️',
            'txt': '📝',
            
            # 压缩文件
            'zip': '📦',
            'rar': '📦',
            'tar': '📦',
            '7z': '📦',
            'gz': '📦',
            
            # 代码文件
            'py': '🐍',
            'java': '☕',
            'js': '📜',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            
            # 系统文件
            'exe': '⚙️',
            'msi': '⚙️',
            'dmg': '⚙️',
            'iso': '💿',
            'img': '💿',
            
            # 默认文件
            'default': '📄',
            'directory': '📁'
        }

    def get_file_type(self, filename: str) -> str:
        """根据文件名获取文件类型"""
        if '.' not in filename:
            return 'default'
        ext = filename.split('.')[-1].lower()
        return ext if ext in self.file_icons else 'default'

    def get_file_icon(self, filename: str, is_dir: bool = False) -> str:
        """获取文件图标"""
        if is_dir:
            return self.file_icons['directory']
        return self.file_icons.get(self.get_file_type(filename), self.file_icons['default'])

    def encode_path(self, path: str) -> str:
        """对路径进行URL编码，保留斜杠和中文"""
        # 分割路径并单独编码每个部分
        parts = path.split('/')
        encoded_parts = []
        for part in parts:
            if part:
                # 对空格进行特殊处理，替换为 %20
                part = part.replace(' ', '%20')
                # 其他特殊字符不编码
                encoded_parts.append(part)
        return '/' + '/'.join(encoded_parts)

    def get_file_list(self, path: str = '/', retry_count: int = 0) -> Optional[Dict]:
        """获取指定路径下的文件列表"""
        api_url = f"{self.base_url}/api/fs/list"
        
        # 对路径进行处理
        processed_path = path.replace(' ', '%20')
        
        data = {
            "path": processed_path,
            "password": "",
            "page": 1,
            "per_page": 100,
            "refresh": False
        }
        
        try:
            if retry_count > 0:
                time.sleep(self.retry_delay)
            
            response = self.session.post(api_url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != 200:
                error_msg = result.get('message', '未知错误')
                if '密码' in error_msg or 'password' in error_msg.lower():
                    for password in ['123456', '666666', '000000']:
                        data['password'] = password
                        response = self.session.post(api_url, json=data)
                        result = response.json()
                        if result.get('code') == 200:
                            return result
                
                # 如果使用 %20 失败，尝试使用 +
                if 'storage not found' in error_msg:
                    data['path'] = path.replace(' ', '+')
                    response = self.session.post(api_url, json=data)
                    result = response.json()
                    if result.get('code') == 200:
                        return result
                
                raise requests.exceptions.RequestException(f"API返回错误: {error_msg}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"获取路径 '{path}' 的文件列表时发生错误: {e}")
            
            if retry_count < self.max_retries:
                print(f"等待 {self.retry_delay} 秒后重试... (第 {retry_count + 1} 次重试)")
                return self.get_file_list(path, retry_count + 1)
            
            return {
                'code': 200,
                'message': 'success',
                'data': {
                    'content': [],
                    'total': 0
                }
            }

    def get_file_url(self, path: str, retry_count: int = 0) -> Optional[str]:
        """获取文件的下载链接"""
        api_url = f"{self.base_url}/api/fs/get"
        
        # 对路径进行处理
        processed_path = path.replace(' ', '%20')
        
        data = {
            "path": processed_path,
            "password": ""
        }
        
        try:
            response = self.session.post(api_url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != 200:
                # 如果 %20 失败，尝试使用 +
                data['path'] = path.replace(' ', '+')
                response = self.session.post(api_url, json=data)
                result = response.json()
                
                if result.get('code') != 200:
                    raise requests.exceptions.RequestException(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result.get('data', {}).get('raw_url')
            
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                print(f"等待 {self.retry_delay} 秒后重试... (第 {retry_count + 1} 次重试)")
                time.sleep(self.retry_delay)
                return self.get_file_url(path, retry_count + 1)
            
            return None

    def print_file_list(self, path: str = '/', depth: int = 0, max_depth: int = -1, get_urls: bool = False):
        """递归打印文件列表，可选择是否获取文件URL"""
        result = self.get_file_list(path)
        indent = "  " * depth
        
        content = result.get('data', {}).get('content', [])
        
        # 打印当前路径
        if depth == 0 or len(content) > 0:  # 只在根目录或有内容时显示路径
            print(f"\n{indent}📂 路径: {path}")
            print(f"{indent}" + "-" * 30)
        
        try:
            for item in content:
                is_dir = item['is_dir']
                name = item['name']
                current_path = f"{path.rstrip('/')}/{name}"
                
                # 获取文件图标
                icon = self.get_file_icon(name, is_dir)
                
                # 打印当前项目
                size_str = f" ({self.format_size(item.get('size', 0))})" if not is_dir else ""
                print(f"{indent}{icon} {name}{size_str}")
                
                # 如果是文件且需要获取URL
                if not is_dir and get_urls:
                    file_url = self.get_file_url(current_path)
                    if file_url:
                        print(f"{indent}  🔗 URL: {file_url}")
                    else:
                        print(f"{indent}  ❌ URL获取失败")
                
                # 如果是目录且未达到最大深度，则递归获取
                if is_dir and (max_depth == -1 or depth < max_depth):
                    sub_result = self.get_file_list(current_path)
                    if sub_result and sub_result.get('data', {}).get('content'):
                        self.print_file_list(current_path, depth + 1, max_depth, get_urls)
                    else:
                        print(f"{indent}  ⚠️ 目录为空或无法访问")
            
            if depth == 0:
                print(f"\n总计: {len(content)} 个项目")
                
        except Exception as e:
            print(f"{indent}处理文件列表时发生错误: {e}")

    def format_size(self, size_in_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f}{unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f}PB"

    def get_all_files_info(self, path: str = '/', include_dirs: bool = False, depth: int = 0, max_depth: int = -1) -> List[Dict]:
        """获取所有文件的信息（包括URL）"""
        result = self.get_file_list(path)
        files_info = []
        
        content = result.get('data', {}).get('content', [])
        
        try:
            for item in content:
                is_dir = item['is_dir']
                name = item['name']
                current_path = f"{path.rstrip('/')}/{name}"
                
                if is_dir:
                    if include_dirs:
                        files_info.append({
                            'name': name,
                            'path': current_path,
                            'encoded_path': self.encode_path(current_path),  # 添加编码后的路径
                            'type': 'directory',
                            'icon': self.get_file_icon(name, True),
                            'accessible': True  # 添加可访问性标记
                        })
                    if max_depth == -1 or depth < max_depth:
                        try:
                            sub_result = self.get_file_list(current_path)
                            if sub_result and sub_result.get('data', {}).get('content'):
                                sub_files = self.get_all_files_info(
                                    current_path, 
                                    include_dirs,
                                    depth + 1,
                                    max_depth
                                )
                                files_info.extend(sub_files)
                            else:
                                # 更新目录的可访问性状态
                                if include_dirs:
                                    for f in files_info:
                                        if f['path'] == current_path:
                                            f['accessible'] = False
                                            break
                        except Exception as e:
                            print(f"获取目录 '{current_path}' 时发生错误: {e}")
                else:
                    try:
                        file_url = self.get_file_url(current_path)
                        file_type = self.get_file_type(name)
                        file_info = {
                            'name': name,
                            'path': current_path,
                            'encoded_path': self.encode_path(current_path),  # 添加编码后的路径
                            'type': file_type,
                            'icon': self.get_file_icon(name, False),
                            'size': item.get('size', 0),
                            'size_formatted': self.format_size(item.get('size', 0)),
                            'modified': item.get('modified', ''),
                            'url': file_url,
                            'accessible': bool(file_url)  # 根据是否能获取URL判断可访问性
                        }
                        files_info.append(file_info)
                    except Exception as e:
                        print(f"获取文件 '{current_path}' 信息时发生错误: {e}")
                        
        except Exception as e:
            print(f"处理路径 '{path}' 时发生错误: {e}")
        
        return files_info

def main():
    alist_url = "https://pan.xiaolibai.cn"
    client = AlistClient(alist_url, max_retries=5, retry_delay=1.0)
    
    # 设置最大递归深度
    max_depth = 4
    
    print(f"开始获取文件列表 (最大深度: {max_depth if max_depth != -1 else '无限'})")
    print("注意: ⚠️ 标记表示无法访问的目录")
    
    # 方式1：打印文件列表并显示URL
    client.print_file_list('/', depth=0, max_depth=max_depth, get_urls=True)
    
    # 方式2：获取所有文件信息（包括URL）并保存到JSON文件
    print("\n正在获取所有文件信息...")
    all_files = client.get_all_files_info('/', include_dirs=True, max_depth=max_depth)
    
    if all_files:
        # 保存到JSON文件
        with open('files_info.json', 'w', encoding='utf-8') as f:
            json.dump(all_files, f, ensure_ascii=False, indent=2)
        print(f"文件信息已保存到 files_info.json (共 {len(all_files)} 个项目)")
    else:
        print("未获取到任何文件信息")

if __name__ == "__main__":
    main() 