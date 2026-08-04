document.addEventListener('DOMContentLoaded', () => {
  // State Initialization
  const state = {
    currentTab: 'bai1',
    currentSubTab: 'kt_all',
    showAnswers: false, // Default: Ẩn đáp án (Study mode)
    userAnswers: JSON.parse(localStorage.getItem('lms_user_answers') || '{}'),
    activeFilter: 'all',
    searchQuery: '',
    theme: localStorage.getItem('lms_theme') || 'light'
  };

  // DOM Element Selectors
  const masterToggle = document.getElementById('masterAnswerToggle');
  const toggleText = document.getElementById('toggleText');
  const toggleIcon = document.getElementById('toggleIcon');
  const themeBtn = document.getElementById('themeToggleBtn');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const subTabBtns = document.querySelectorAll('.sub-tab-btn');
  const ktSubTabsContainer = document.getElementById('ktSubTabs');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const questionsContainer = document.getElementById('questionsContainer');
  const questionGrid = document.getElementById('questionGrid');
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toastMessage');

  // Single Top Reset Button
  const resetCurrentTabBtn = document.getElementById('resetCurrentTabBtn');

  // Stats DOM Elements
  const statCorrectCount = document.getElementById('statCorrectCount');
  const statWrongCount = document.getElementById('statWrongCount');
  const statUnansweredCount = document.getElementById('statUnansweredCount');
  const overallScoreBadge = document.getElementById('overallScoreBadge');
  const overallProgressFill = document.getElementById('overallProgressFill');
  const filterAllCount = document.getElementById('filterAllCount');
  const filterWrongCount = document.getElementById('filterWrongCount');
  const filterCorrectCount = document.getElementById('filterCorrectCount');
  const filterUnansweredCount = document.getElementById('filterUnansweredCount');

  // Set initial theme
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();

  // Helper to get active questions for current tab / subtab
  function getActiveQuestions() {
    if (!window.QUIZ_DATA) return [];

    if (state.currentTab === 'bai1') return window.QUIZ_DATA.bai1.questions.map(q => ({ ...q, sourceTab: 'bai1' }));
    if (state.currentTab === 'bai2') return window.QUIZ_DATA.bai2.questions.map(q => ({ ...q, sourceTab: 'bai2' }));
    if (state.currentTab === 'bai3') return window.QUIZ_DATA.bai3.questions.map(q => ({ ...q, sourceTab: 'bai3' }));
    
    if (state.currentTab === 'kt') {
      const q1 = window.QUIZ_DATA.kt1.questions.map(q => ({ ...q, sourceTab: 'kt1', prefix: 'KT1 - ' }));
      const q2 = window.QUIZ_DATA.kt2.questions.map(q => ({ ...q, sourceTab: 'kt2', prefix: 'KT2 - ' }));
      const q3 = window.QUIZ_DATA.kt3.questions.map(q => ({ ...q, sourceTab: 'kt3', prefix: 'KT3 - ' }));

      if (state.currentSubTab === 'kt1') return q1;
      if (state.currentSubTab === 'kt2') return q2;
      if (state.currentSubTab === 'kt3') return q3;
      return [...q1, ...q2, ...q3];
    }
    return [];
  }

  // Get question unique ID key for userAnswers storage
  function getQKey(q) {
    return `${q.sourceTab}_${q.question_id}`;
  }

  // Toast Notification Trigger
  function showToast(msg) {
    toastMessage.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  // Render Page Content
  function render() {
    const questions = getActiveQuestions();
    updateToggleLabel();
    renderQuestions(questions);
    renderSidebarGrid(questions);
    updateStats(questions);
  }

  // Update Toggle Switch Label based on State
  function updateToggleLabel() {
    if (state.showAnswers) {
      toggleText.textContent = "Chế độ Xem Đáp Án & Chữa Bài (Hiện đáp án)";
      toggleIcon.className = "fa-solid fa-eye";
    } else {
      toggleText.textContent = "Chế độ Ôn Luyện (Ẩn đáp án)";
      toggleIcon.className = "fa-solid fa-eye-slash";
    }
  }

  // Render Questions Cards
  function renderQuestions(questions) {
    questionsContainer.innerHTML = '';

    // Filter questions
    const filtered = questions.filter(q => {
      const qKey = getQKey(q);
      const userChoice = state.showAnswers ? q.selected_option : state.userAnswers[qKey];
      const isAnswered = !!userChoice;
      const isCorrect = userChoice === q.correct_option;

      // Filter by status button
      if (state.activeFilter === 'wrong' && (!isAnswered || isCorrect)) return false;
      if (state.activeFilter === 'correct' && (!isAnswered || !isCorrect)) return false;
      if (state.activeFilter === 'unanswered' && isAnswered) return false;

      // Filter by search query
      if (state.searchQuery.trim()) {
        const query = state.searchQuery.toLowerCase();
        const matchQ = q.question.toLowerCase().includes(query);
        const matchOpt = q.options.some(o => o.text.toLowerCase().includes(query));
        if (!matchQ && !matchOpt) return false;
      }

      return true;
    });

    if (filtered.length === 0) {
      questionsContainer.innerHTML = `
        <div class="empty-state" style="text-align: center; padding: 40px; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
          <i class="fa-solid fa-folder-open" style="font-size: 3rem; color: var(--text-light); margin-bottom: 12px;"></i>
          <h3>Không tìm thấy câu hỏi phù hợp</h3>
          <p style="color: var(--text-muted);">Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm.</p>
        </div>
      `;
      return;
    }

    filtered.forEach((q, idx) => {
      const qKey = getQKey(q);
      const userChoice = state.showAnswers ? q.selected_option : state.userAnswers[qKey];
      const isAnswered = !!userChoice;
      const isUserCorrect = userChoice === q.correct_option;
      const displayId = q.prefix ? `${q.prefix}Câu ${q.question_id}` : `Câu ${q.question_id}`;

      const card = document.createElement('div');
      card.className = `question-card ${isAnswered ? (isUserCorrect ? 'correct-border' : 'wrong-border') : ''}`;
      card.id = `qcard_${qKey}`;

      // Card Header
      let headerHTML = `
        <div class="question-header">
          <div class="question-title-box">
            <span class="question-badge">${displayId}</span>
            <div class="question-text">${q.question}</div>
          </div>
        </div>
      `;

      // Options List
      let optionsHTML = `<div class="options-list">`;
      q.options.forEach(opt => {
        const isSelectedByUser = userChoice === opt.label;
        const isTrueCorrect = opt.label === q.correct_option;

        let optClass = 'option-item';
        let badgeHTML = '';

        if (state.showAnswers) {
          // Master Show Answers Mode
          if (isTrueCorrect) {
            optClass += ' is-correct-answer';
            badgeHTML += `<span class="option-badge badge-correct"><i class="fa-solid fa-check"></i> Đáp án đúng chuẩn</span>`;
          }
          if (q.selected_option === opt.label) {
            if (q.selected_option !== q.correct_option) {
              optClass += ' is-wrong-answer';
              badgeHTML += `<span class="option-badge badge-user-wrong"><i class="fa-solid fa-xmark"></i> Lựa chọn cũ của bạn (Chưa đúng)</span>`;
            } else {
              badgeHTML += `<span class="option-badge badge-user-choice"><i class="fa-solid fa-user-check"></i> Lựa chọn của bạn</span>`;
            }
          }
        } else {
          // Practice Mode (Ẩn đáp án)
          if (isAnswered) {
            if (isSelectedByUser) {
              if (isTrueCorrect) {
                optClass += ' is-correct-answer';
                badgeHTML = `<span class="option-badge badge-correct"><i class="fa-solid fa-check"></i> Chọn đúng!</span>`;
              } else {
                optClass += ' is-wrong-answer';
                badgeHTML = `<span class="option-badge badge-user-wrong"><i class="fa-solid fa-xmark"></i> Chọn sai!</span>`;
              }
            } else if (isTrueCorrect && !isUserCorrect) {
              optClass += ' is-correct-answer';
              badgeHTML = `<span class="option-badge badge-correct"><i class="fa-solid fa-check"></i> Đáp án đúng chuẩn</span>`;
            }
          }
        }

        optionsHTML += `
          <div class="${optClass}" data-qkey="${qKey}" data-label="${opt.label}">
            <div class="option-label">${opt.label}</div>
            <div class="option-text">${opt.text}</div>
            ${badgeHTML}
          </div>
        `;
      });
      optionsHTML += `</div>`;

      // Explanation Box
      let explanationHTML = '';
      if (state.showAnswers || isAnswered) {
        const boxClass = isUserCorrect ? 'correct' : 'wrong';
        const expText = q.explanation || (isUserCorrect ? 
          `✅ **Đáp án đúng là ${q.correct_option}** theo chuẩn kiến thức Triết học Mác - Lênin.` : 
          `❌ **Đáp án chuẩn là ${q.correct_option}**. Lựa chọn ${userChoice} chưa chính xác.`);
        
        explanationHTML = `
          <div class="explanation-box ${boxClass}">
            <div class="explanation-title">
              <i class="fa-solid ${isUserCorrect ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
              ${isUserCorrect ? 'Giải thích đáp án đúng:' : 'Phân tích & Hướng dẫn chữa câu sai:'}
            </div>
            <div class="explanation-content">${formatMarkdown(expText)}</div>
          </div>
        `;
      }

      card.innerHTML = headerHTML + optionsHTML + explanationHTML;
      questionsContainer.appendChild(card);
    });

    // Attach click events on options in Practice mode
    if (!state.showAnswers) {
      document.querySelectorAll('.option-item').forEach(optEl => {
        optEl.addEventListener('click', (e) => {
          const qKey = optEl.dataset.qkey;
          const label = optEl.dataset.label;
          state.userAnswers[qKey] = label;
          localStorage.setItem('lms_user_answers', JSON.stringify(state.userAnswers));
          render();
        });
      });
    }
  }

  // Formatting helper
  function formatMarkdown(txt) {
    if (!txt) return '';
    return txt
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  // Sidebar Grid
  function renderSidebarGrid(questions) {
    questionGrid.innerHTML = '';

    questions.forEach((q, idx) => {
      const qKey = getQKey(q);
      const userChoice = state.showAnswers ? q.selected_option : state.userAnswers[qKey];
      const isAnswered = !!userChoice;
      const isCorrect = userChoice === q.correct_option;

      const item = document.createElement('button');
      item.className = 'grid-item';

      if (isAnswered) {
        if (isCorrect) item.classList.add('correct');
        else item.classList.add('wrong');
      }

      item.textContent = idx + 1;
      item.title = `Câu ${idx + 1}: ${q.question.substring(0, 40)}...`;

      item.addEventListener('click', () => {
        const card = document.getElementById(`qcard_${qKey}`);
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('highlight');
          setTimeout(() => card.classList.remove('highlight'), 1500);
        }
      });

      questionGrid.appendChild(item);
    });
  }

  // Update Stats
  function updateStats(questions) {
    let total = questions.length;
    let correct = 0;
    let wrong = 0;
    let unanswered = 0;

    questions.forEach(q => {
      const qKey = getQKey(q);
      const userChoice = state.showAnswers ? q.selected_option : state.userAnswers[qKey];
      if (!userChoice) {
        unanswered++;
      } else if (userChoice === q.correct_option) {
        correct++;
      } else {
        wrong++;
      }
    });

    const percent = total > 0 ? Math.round((correct / total) * 100) : 0;

    statCorrectCount.textContent = correct;
    statWrongCount.textContent = wrong;
    statUnansweredCount.textContent = unanswered;
    overallScoreBadge.textContent = `${correct} / ${total} (${percent}%)`;
    overallProgressFill.style.width = `${percent}%`;

    filterAllCount.textContent = total;
    filterWrongCount.textContent = wrong;
    filterCorrectCount.textContent = correct;
    filterUnansweredCount.textContent = unanswered;
  }

  // RESET FUNCTION: Resets the active tab questions
  function resetActiveTabAnswers() {
    const currentQuestions = getActiveQuestions();
    let resetCount = 0;
    currentQuestions.forEach(q => {
      const qKey = getQKey(q);
      if (state.userAnswers[qKey]) {
        delete state.userAnswers[qKey];
        resetCount++;
      }
    });
    localStorage.setItem('lms_user_answers', JSON.stringify(state.userAnswers));
    render();
    
    let tabName = "Bài 1";
    if (state.currentTab === 'bai2') tabName = "Bài 2";
    if (state.currentTab === 'bai3') tabName = "Bài 3";
    if (state.currentTab === 'kt') tabName = "Bài Kiểm Tra";

    showToast(`Đã làm lại ${tabName}!`);
  }

  // Single Top Reset Button Event Listener
  if (resetCurrentTabBtn) {
    resetCurrentTabBtn.addEventListener('click', resetActiveTabAnswers);
  }

  // Master Toggle Change Handler
  masterToggle.addEventListener('change', (e) => {
    state.showAnswers = e.target.checked;
    render();
  });

  // Tab Buttons Click Handler
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      state.currentTab = btn.dataset.tab;
      if (state.currentTab === 'kt') {
        ktSubTabsContainer.style.display = 'flex';
      } else {
        ktSubTabsContainer.style.display = 'none';
      }
      render();
    });
  });

  // Sub-tab Buttons Click Handler
  subTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      subTabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.currentSubTab = btn.dataset.subtab;
      render();
    });
  });

  // Filter Buttons Click Handler
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeFilter = btn.dataset.filter;
      render();
    });
  });

  // Search Input Handler
  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    clearSearchBtn.style.display = state.searchQuery ? 'block' : 'none';
    render();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearSearchBtn.style.display = 'none';
    render();
  });

  // Theme Toggle Handler
  themeBtn.addEventListener('click', () => {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('lms_theme', state.theme);
    updateThemeIcon();
  });

  function updateThemeIcon() {
    themeBtn.innerHTML = state.theme === 'light' ? 
      '<i class="fa-solid fa-moon"></i>' : 
      '<i class="fa-solid fa-sun"></i>';
  }

  // Initial Render
  render();
});
