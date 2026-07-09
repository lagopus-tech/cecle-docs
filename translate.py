import os
import re
import requests

# ================== 🌟 业务员核心配置区域 ==================
# 1. 填入你的 DeepSeek API Key（后续也可在 Cloudflare 环境变量里安全绑定）
DEEPSEEK_API_KEY = os.environ.get("LLM_API_KEY")

# DeepSeek 官方标准端点与模型名称
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"  # 指向极度聪明的 DeepSeek-V3 模型

# 2. 你的 Shopify 官网主域名 (🌟请改成你们机械站的实际域名，不要带 https:// 和末尾斜杠)
SHOPIFY_DOMAIN = "cecle.net" 

# 3. Shopify Markets 小语言路径映射表（对应你在 Shopify 后台 Market 开启的语言子目录）
SHOPIFY_LANG_MAPPING = {
    'zh': 'zh',      # 简体中文 -> www.cecle.net/zh/
    'es': 'es',      # 西班牙语 -> www.cecle.net/es/
    'fr': 'fr',      # 法语
    'pt': 'pt',      # 葡萄牙语（如果是巴西站通常也是 /pt 或 /pt-br，根据实际修改）
    'ar': 'ar',      # 阿拉伯语
    'id': 'id',      # 印尼语
    'vi': 'vi',      # 越南语
    'th': 'th',      # 泰语
    'pl': 'pl',      # 波兰语
    'de': 'de',      # 德语
    'ru': 'ru',      # 俄语
    'tr': 'tr',      # 土耳其语
    'it': 'it'       # 意大利语
}
# ==========================================================

# 定义 14 种目标语言全称
LANGUAGES = {
    'zh': 'Simplified Chinese',
    'es': 'Spanish',
    'fr': 'French',
    'pt': 'Brazilian Portuguese',
    'ar': 'Arabic',
    'id': 'Indonesian',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'pl': 'Polish',
    'de': 'German',
    'ru': 'Russian',
    'tr': 'Turkish',
    'it': 'Italian'
}

def localize_shopify_links(markdown_content, lang_code):
    """
    【核心路由后处理】强制将 Markdown 中的英文官网链接转换为对应小语言站链接
    例如: https://www.cecle.net/products/abc -> https://www.cecle.net/es/products/abc
    """
    if not SHOPIFY_DOMAIN:
        return markdown_content
    
    lang_path = SHOPIFY_LANG_MAPPING.get(lang_code, lang_code)
    
    # 正则匹配形如 http://域名/ 或 https://域名/ 的结构
    pattern = rf'(https?://(?:www\.)?{re.escape(SHOPIFY_DOMAIN)}/)'
    
    def replace_match(match):
        full_match = match.group(0)
        start_idx = match.end()
        # 双重保险：检查后面是不是已经跟着当前的语言路径了，防止重复注入变成 /es/es/
        if markdown_content[start_idx:start_idx+len(lang_path)+1] == f"{lang_path}/":
            return full_match
        return f"{full_match}{lang_path}/"
    
    return re.sub(pattern, replace_match, markdown_content)

def translate_text_via_deepseek(text, target_lang):
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "YOUR_DEEPSEEK_API_KEY_HERE":
        print("提示: 未检测到有效的 DEEPSEEK_API_KEY，跳过实际翻译。")
        return text
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 针对包装与食品机械行业的终极工业级 Prompt
    prompt = (
        f"You are an expert technical translator specializing in packaging machinery and food processing industries. "
        f"Translate the following Markdown document into {target_lang}.\n\n"
        f"CRITICAL RULES:\n"
        f"1. Preserve ALL Markdown syntax, HTML tags, image tags (![alt](url)), and code blocks EXACTLY.\n"
        f"2. DO NOT translate or modify ANY URL links, paths, or image sources within parentheses (e.g., in [text](url), ONLY translate the 'text', NEVER touch the 'url').\n"
        f"3. Maintain all technical specifications, metrics, numbers, and units (e.g., '304 stainless steel', 'V', 'Hz', 'kW', 'pcs/min') precisely as in the original.\n"
        f"4. Output ONLY the raw translated Markdown content. Do not include any explanations, introductions, or pleasantries."
    )
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1  # 极低的随机性，确保翻译极其严谨、工业化
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"DeepSeek 翻译失败，状态码: {response.status_code}, 错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"网络请求异常: {e}")
        return None

def main():
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        print("错误：未找到 docs 文件夹，请确认路径是否正确。")
        return

    # 自动遍历 docs 目录，寻找英文原版 .md 文件
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                # 排除已经生成过的小语种文件（如 index.zh.md）
                parts = file.split('.')
                if len(parts) >= 3 and parts[-2] in LANGUAGES:
                    continue
        
                english_file_path = os.path.join(root, file)
                print(f"\n🚀 正在处理英文原版: {english_file_path}")
                
                with open(english_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 循环翻译成 14 种语言
                for lang_code, lang_name in LANGUAGES.items():
                    base_name = ".".join(parts[:-1])
                    translated_file_name = f"{base_name}.{lang_code}.md"
                    translated_file_path = os.path.join(root, translated_file_name)
                    
                    # 如果本地或云端已经有了，就不重复生成，省钱省时间
                    if os.path.exists(translated_file_path):
                        continue
                    
                    print(f"  -> 正在通过 DeepSeek 翻译为 【{lang_name}】...")
                    translated_content = translate_text_via_deepseek(content, lang_name)
                    
                    if translated_content:
                        # 🌟 核心后处理：强制替换独立站官网链接为对应的小语言站点链接
                        final_content = localize_shopify_links(translated_content, lang_code)
                        
                        with open(translated_file_path, "w", encoding="utf-8") as f_out:
                            f_out.write(final_content)
                        print(f"  ✅ 成功生成并路由链接: {translated_file_name}")

if __name__ == "__main__":
    main()