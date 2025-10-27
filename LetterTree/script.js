// 难度配置
const difficultyConfig = {
    1: { letterCount: 5, displayTime: 2000, letterSpacing: 100 },  // 简单
    2: { letterCount: 7, displayTime: 1500, letterSpacing: 140 },  // 中等
    3: { letterCount: 9, displayTime: 1000, letterSpacing: 170 },  // 困难
    4: { letterCount: 11, displayTime: 800, letterSpacing: 200 }   // 极难
};

let currentRow = null;
let currentShownLetters = null; // 实际显示的字母
let currentAnswer = null;

// DOM元素
const startBtn = document.getElementById('startBtn');
const showAnswerBtn = document.getElementById('showAnswerBtn');
const submitBtn = document.getElementById('submitBtn');
const viewport = document.getElementById('viewport');
const answerSection = document.getElementById('answerSection');
const leftLetterInput = document.getElementById('leftLetter');
const rightLetterInput = document.getElementById('rightLetter');
const result = document.getElementById('result');
const difficultySelect = document.getElementById('difficulty');

// 开始练习
startBtn.addEventListener('click', () => {
    if (viewport.classList.contains('locked')) {
        return;
    }
    
    startPractice();
});

// 显示答案
showAnswerBtn.addEventListener('click', () => {
    showAnswer();
});

// 提交答案
submitBtn.addEventListener('click', () => {
    checkAnswer();
});

// 回车键提交
leftLetterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        rightLetterInput.focus();
    }
});

rightLetterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        checkAnswer();
    }
});

// 开始练习
function startPractice() {
    // 隐藏答案区域
    answerSection.style.display = 'none';
    result.style.display = 'none';
    showAnswerBtn.style.display = 'none';
    
    // 清空输入框
    leftLetterInput.value = '';
    rightLetterInput.value = '';
    
    // 获取难度配置
    const difficulty = parseInt(difficultySelect.value);
    const config = difficultyConfig[difficulty];
    
    // 设置当前行（不需要数字，使用点作为视点）
    currentRow = {};
    
    // 显示中间的点
    viewport.classList.add('locked');
    viewport.innerHTML = `<div class="letters"><div class="center-point">·</div></div>`;
    
    // 延迟后显示字母
    setTimeout(() => {
        showLetters(config);
    }, 500);
}

// 显示字母
function showLetters(config) {
    const letters = generateLetters(config.letterCount);
    
    // 保存显示的字母（用于验证）
    currentShownLetters = {
        left: letters.left.join(''),
        right: letters.right.join('')
    };
    
    // 设置字母与视点的间隔
    document.documentElement.style.setProperty('--letter-spacing', config.letterSpacing + 'px');
    
    // 构建显示内容
    let html = '<div class="letters">';
    
    // 左侧字母组（字母之间没有间隔，只在最后与数字保持间隔）
    html += '<div class="letter-group left-group">';
    for (let i = 0; i < letters.left.length; i++) {
        html += `<div class="letter">${letters.left[i]}</div>`;
    }
    html += '</div>';
    
    // 中间点（与左右字母组保持间隔）
    html += `<div class="center-point">·</div>`;
    
    // 右侧字母组（字母之间没有间隔，只在开始与数字保持间隔）
    html += '<div class="letter-group right-group">';
    for (let i = 0; i < letters.right.length; i++) {
        html += `<div class="letter">${letters.right[i]}</div>`;
    }
    html += '</div>';
    
    html += '</div>';
    
    viewport.innerHTML = html;
    viewport.classList.add('fade-in');
    
    // 根据难度设置显示时间
    setTimeout(() => {
        hideLetters();
    }, config.displayTime);
}

// 生成随机字母位置
function generateLetters(count) {
    const leftCount = Math.floor(count / 2);
    const rightCount = Math.floor(count / 2);
    
    // 如果总数是奇数，随机分配到一侧
    const extra = count % 2;
    const leftExtra = Math.floor(Math.random() * 2);
    
    const finalLeftCount = leftCount + (leftExtra * extra);
    const finalRightCount = rightCount + ((1 - leftExtra) * extra);
    
    return {
        left: new Array(finalLeftCount).fill(null).map(() => getRandomLetter()),
        right: new Array(finalRightCount).fill(null).map(() => getRandomLetter())
    };
}

// 获取随机字母
function getRandomLetter() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    return letters[Math.floor(Math.random() * letters.length)];
}

// 隐藏字母
function hideLetters() {
    viewport.classList.add('fade-out');
    
    setTimeout(() => {
        viewport.innerHTML = `<div class="letters"><div class="center-point">·</div></div>`;
        viewport.classList.remove('fade-in', 'fade-out', 'locked');
        
        // 重置CSS变量
        document.documentElement.style.setProperty('--letter-spacing', '40px');
        
        // 显示答案输入区域
        answerSection.style.display = 'block';
        showAnswerBtn.style.display = 'block';
        
        // 清除正确答案（为安全起见）
        currentAnswer = null;
        
        // 聚焦到左侧输入框
        leftLetterInput.focus();
    }, 300);
}

// 显示答案
function showAnswer() {
    if (currentShownLetters) {
        leftLetterInput.value = currentShownLetters.left;
        rightLetterInput.value = currentShownLetters.right;
        
        leftLetterInput.style.background = '#d4edda';
        rightLetterInput.style.background = '#d4edda';
        
        setTimeout(() => {
            leftLetterInput.style.background = 'white';
            rightLetterInput.style.background = 'white';
        }, 1000);
    }
}

// 检查答案
function checkAnswer() {
    const userLeft = leftLetterInput.value.trim().toUpperCase();
    const userRight = rightLetterInput.value.trim().toUpperCase();
    
    const correctLeft = currentShownLetters.left;
    const correctRight = currentShownLetters.right;
    
    let isCorrect = false;
    let message = '';
    
    // 检查答案是否正确（允许顺序不同）
    if (userLeft === correctLeft && userRight === correctRight) {
        isCorrect = true;
        message = '✓ 完全正确！';
    } else if (userLeft === correctRight && userRight === correctLeft) {
        isCorrect = true;
        message = '✓ 完全正确！（左右交换）';
    } else {
        isCorrect = false;
        message = `✗ 不正确！正确答案：左侧=${correctLeft}, 右侧=${correctRight}`;
    }
    
    // 显示结果
    result.className = isCorrect ? 'result correct' : 'result incorrect';
    result.textContent = message;
    result.style.display = 'block';
    
    // 高亮输入框
    if (isCorrect) {
        leftLetterInput.style.background = '#d4edda';
        rightLetterInput.style.background = '#d4edda';
    } else {
        leftLetterInput.style.background = '#f8d7da';
        rightLetterInput.style.background = '#f8d7da';
    }
    
    // 清除背景色
    setTimeout(() => {
        leftLetterInput.style.background = 'white';
        rightLetterInput.style.background = 'white';
    }, 2000);
}
