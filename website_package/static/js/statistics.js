// 統計學講義功能腳本
document.addEventListener('DOMContentLoaded', function() {
    // 添加目錄導航
    buildTableOfContents();
    
    // 添加答案顯示/隱藏功能
    setupAnswerToggle();
});

// 建立目錄
function buildTableOfContents() {
    const toc = document.querySelector('.toc');
    if (!toc) return;
    
    const headings = document.querySelectorAll('h3');
    if (headings.length > 0) {
        const tocList = document.createElement('ul');
        headings.forEach(heading => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `#${heading.id}`;
            a.textContent = heading.textContent;
            li.appendChild(a);
            tocList.appendChild(li);
        });
        toc.appendChild(tocList);
    }
}

// 設置答案切換功能
function setupAnswerToggle() {
    const answers = document.querySelectorAll('.answer');
    answers.forEach(answer => {
        const questionText = answer.previousElementSibling;
        if (questionText && questionText.classList.contains('question')) {
            // 初始隱藏答案
            answer.style.display = 'none';
            
            // 添加切換按鈕
            const toggleBtn = document.createElement('button');
            toggleBtn.textContent = '顯示答案';
            toggleBtn.className = 'toggle-answer';
            toggleBtn.style.marginLeft = '10px';
            toggleBtn.style.padding = '3px 8px';
            toggleBtn.style.background = '#f0f0f0';
            toggleBtn.style.border = '1px solid #ddd';
            toggleBtn.style.borderRadius = '3px';
            toggleBtn.style.cursor = 'pointer';
            
            questionText.appendChild(toggleBtn);
            
            // 綁定點擊事件
            toggleBtn.addEventListener('click', function() {
                if (answer.style.display === 'none') {
                    answer.style.display = 'block';
                    this.textContent = '隱藏答案';
                } else {
                    answer.style.display = 'none';
                    this.textContent = '顯示答案';
                }
            });
        }
    });
}
