(function() {
    const referrer = document.referrer;
    const currentPath = window.location.pathname;
    
    // 13 种目标语种代码（不含默认的英文 en）
    const languages = ['zh', 'es', 'fr', 'pt', 'ar', 'id', 'vi', 'th', 'pl', 'de', 'ru', 'tr', 'it'];
    
    // 检查当前页面是否已经是多语言页面（防止死循环跳转）
    const isAlreadyLocalized = languages.some(lang => currentPath.startsWith('/' + lang + '/'));
    
    // 如果当前是英文默认页，且用户是从带有语种路径的独立站跳转过来的
    if (!isAlreadyLocalized && referrer) {
        // 正则匹配独立站域名后的语言路径，形如 cecle.net/es/ 或 cecle.net/zh/
        const match = referrer.match(/cecle\.net\/([a-z]{2}(-[a-z]{2})?)\//i);
        if (match) {
            const detectedLang = match[1].toLowerCase();
            if (languages.includes(detectedLang)) {
                // 瞬间将用户重定向到文档站对应语种的相同页面
                window.location.href = window.location.origin + '/' + detectedLang + currentPath;
            }
        }
    }
})();