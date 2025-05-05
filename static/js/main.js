/**
 * 統計學學習平台主要 JavaScript 檔案
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化 MathJax（如果存在）
    initMathJax();
    
    // 設置程式碼複製功能
    setupCodeCopy();
    
    // 設置滾動監聽
    setupScrollListeners();
    
    // 設置章節進度追蹤
    setupProgressTracking();
    
    // 初始化練習題互動功能
    initExerciseInteractions();
});

/**
 * 初始化工具提示
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 初始化 MathJax（若存在）
 */
function initMathJax() {
    if (typeof MathJax !== 'undefined') {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }
}

/**
 * 設置程式碼複製功能
 */
function setupCodeCopy() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        // 建立複製按鈕
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-secondary code-copy-btn';
        copyButton.innerText = '複製';
        
        // 定位按鈕
        const pre = block.parentNode;
        pre.style.position = 'relative';
        pre.appendChild(copyButton);
        
        // 設置複製事件
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                copyButton.innerText = '已複製!';
                setTimeout(() => {
                    copyButton.innerText = '複製';
                }, 2000);
            }).catch(err => {
                console.error('複製失敗:', err);
                copyButton.innerText = '複製失敗';
                setTimeout(() => {
                    copyButton.innerText = '複製';
                }, 2000);
            });
        });
    });
}

/**
 * 設置滾動監聽器
 */
function setupScrollListeners() {
    // 監聽章節內容滾動，更新章節側邊目錄高亮
    const sections = document.querySelectorAll('.section-content');
    const tocLinks = document.querySelectorAll('.toc-link');
    
    if (sections.length > 0 && tocLinks.length > 0) {
        window.addEventListener('scroll', () => {
            let currentSectionId = '';
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                
                if (window.scrollY >= sectionTop - 100 && 
                    window.scrollY < sectionTop + sectionHeight - 100) {
                    currentSectionId = section.getAttribute('id');
                }
            });
            
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${currentSectionId}`) {
                    link.classList.add('active');
                }
            });
        });
    }
}

/**
 * 設置章節進度追蹤
 */
function setupProgressTracking() {
    // 簡單的進度追蹤 - 將瀏覽過的章節存入 localStorage
    const chapterLinks = document.querySelectorAll('.chapter-link');
    
    chapterLinks.forEach(link => {
        link.addEventListener('click', () => {
            const chapterId = link.getAttribute('data-chapter-id');
            if (chapterId) {
                // 讀取已儲存的進度
                let visitedChapters = JSON.parse(localStorage.getItem('visitedChapters') || '[]');
                
                // 添加當前章節（如果尚未添加）
                if (!visitedChapters.includes(chapterId)) {
                    visitedChapters.push(chapterId);
                    localStorage.setItem('visitedChapters', JSON.stringify(visitedChapters));
                }
                
                // 更新進度指示器
                updateProgressIndicator();
            }
        });
    });
    
    // 頁面載入時更新進度指示器
    updateProgressIndicator();
}

/**
 * 更新進度指示器
 */
function updateProgressIndicator() {
    const progressBar = document.querySelector('.progress-bar');
    const totalChapters = document.querySelectorAll('.chapter-link').length;
    
    if (progressBar && totalChapters > 0) {
        const visitedChapters = JSON.parse(localStorage.getItem('visitedChapters') || '[]');
        const progress = (visitedChapters.length / totalChapters) * 100;
        
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
}

/**
 * 初始化練習題互動功能
 */
function initExerciseInteractions() {
    // 多選題選項互動
    const quizOptions = document.querySelectorAll('.quiz-option');
    
    quizOptions.forEach(option => {
        option.addEventListener('click', function() {
            // 找到同組的所有選項
            const allOptions = document.querySelectorAll(`[name="${this.querySelector('input').name}"]`);
            
            // 移除所有選項的選中樣式
            allOptions.forEach(opt => {
                opt.parentNode.classList.remove('selected');
            });
            
            // 為當前選項添加選中樣式
            this.classList.add('selected');
        });
    });
} 