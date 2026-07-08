(function() {
    const referrer = document.referrer;
    const currentPath = window.location.pathname;
    const languages = ['zh', 'es', 'fr', 'pt', 'ar', 'id', 'vi', 'th', 'pl', 'de', 'ru', 'tr', 'it'];
    const isAlreadyLocalized = languages.some(lang => currentPath.startsWith('/' + lang + '/'));
    
    if (!isAlreadyLocalized && referrer) {
        const match = referrer.match(/cecle\.net\/([a-z]{2}(-[a-z]{2})?)\//i);
        if (match) {
            const detectedLang = match[1].toLowerCase();
            if (languages.includes(detectedLang)) {
                window.location.href = window.location.origin + '/' + detectedLang + currentPath;
            }
        }
    }
})();