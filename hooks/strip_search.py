import json
import os

def strip_search_index(site_dir="site"):
    for root, dirs, files in os.walk(site_dir):
        if 'search_index.json' in files:
            file_path = os.path.join(root, 'search_index.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 剥离段落 text，只保留标题 title 和链接 location
                for doc in data.get('docs', []):
                    if 'text' in doc:
                        doc['text'] = ''

                # 重新写入紧凑格式的 JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"[后置精简成功] {file_path} 已精简至: {size_mb:.2f} MB")
            except Exception as e:
                print(f"[后置精简失败] 处理 {file_path} 报错: {e}")

def on_post_build(config, **kwargs):
    strip_search_index(config.get('site_dir', 'site'))

if __name__ == '__main__':
    strip_search_index('site')