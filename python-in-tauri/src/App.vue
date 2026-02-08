<template>
  <div id="app" :data-theme="theme">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">📓</div>
          <div class="logo-text">
            <h1>无道翻译</h1>
            <p>AI驱动的实时翻译</p>
          </div>
        </div>
      </div>

      <nav class="nav-menu">
        <div v-for="tab in tabs" :key="tab.id" class="nav-item" :class="{ active: currentTab === tab.id }"
          @click="switchTab(tab.id)">
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="theme-toggle">
          <button class="theme-btn" :class="{ active: theme === 'light' }" @click="setTheme('light')" title="浅色主题">
            <span class="theme-icon">☀️</span>
            <span class="theme-label">浅色</span>
          </button>
          <button class="theme-btn" :class="{ active: theme === 'dark' }" @click="setTheme('dark')" title="暗色主题">
            <span class="theme-icon">🌙</span>
            <span class="theme-label">暗色</span>
          </button>
        </div>
        <div class="user-info">
          <div class="avatar">AI</div>
          <div class="user-details">
            <span class="username">智能助手</span>
            <span class="status" :class="backendStatusClass">{{ backendStatusText }}</span>
          </div>
        </div>

        <!-- 后端状态指示器 -->
        <div class="backend-status" v-if="backendStatus !== 'ready'">
          <div class="status-indicator" :class="backendStatus">
            <span class="status-dot"></span>
            <span class="status-text">{{ backendStatusText }}</span>
          </div>
          <div v-if="backendError" class="error-details">
            <button @click="showErrorDetails" class="error-btn">查看详情</button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <component :is="currentComponent" />
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import ApiTranslation from './components/ApiTranslation.vue';
import Settings from './components/Settings.vue';
import BatchFileTranslation from './components/BatchFileTranslation.vue';
import BatchTextReplace from './components/BatchTextReplace.vue';
import BatchPDFTranslation from './components/BatchPDFTranslation.vue';

export default {
  name: 'App',
  components: {
    ApiTranslation,
    Settings,
    BatchFileTranslation,
    BatchTextReplace,
    BatchPDFTranslation
  },
  setup() {
    const currentTab = ref('api');
    const theme = ref('light');
    const backendStatus = ref('checking');
    const backendError = ref(null);

    const tabs = [
      { id: 'api', label: '智能翻译', component: ApiTranslation, icon: '🤖' },
      { id: 'batch', label: '批量翻译', component: BatchFileTranslation, icon: '📁' },
      { id: 'pdf', label: 'PDF翻译', component: BatchPDFTranslation, icon: '📄' },
      { id: 'replace', label: '批量文本替换', component: BatchTextReplace, icon: '🔄' },
      { id: 'settings', label: '设置', component: Settings, icon: '⚙️' }
    ];

    const currentComponent = computed(() => {
      const tab = tabs.find(t => t.id === currentTab.value);
      return tab ? tab.component : tabs[0].component;
    });

    // 后端状态相关的计算属性
    const backendStatusClass = computed(() => {
      switch (backendStatus.value) {
        case 'ready': return 'status-online';
        case 'checking': return 'status-checking';
        case 'error': return 'status-error';
        default: return 'status-offline';
      }
    });

    const backendStatusText = computed(() => {
      switch (backendStatus.value) {
        case 'ready': return '后端就绪';
        case 'checking': return '检查中...';
        case 'error': return '后端错误';
        default: return '后端离线';
      }
    });

    const switchTab = (tabId) => {
      currentTab.value = tabId;
    };

    // 主题管理
    const setTheme = (newTheme) => {
      theme.value = newTheme;
      localStorage.setItem('app-theme', newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
      // 触发自定义事件，通知 Settings.vue 更新
      window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme: newTheme } }));
    };

    const checkBackendStatus = async (retryCount = 0) => {
      try {
        if (retryCount === 0) {
          backendStatus.value = 'checking';
        }

        let port = 8000;
        try {
          const response = await fetch('./port_config.json');
          if (response.ok) {
            const config = await response.json();
            port = config.port || 8000;
          }
        } catch (e) {
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);

        const response = await fetch(`http://127.0.0.1:${port}/health`, {
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          backendStatus.value = 'ready';
          backendError.value = null;
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (error) {
        // 如果失败，继续重试
        backendStatus.value = 'checking'; // 保持检查状态，避免闪烁

        // 最多重试20次（约40秒），之后显示错误
        if (retryCount < 20) {
          setTimeout(() => checkBackendStatus(retryCount + 1), 2000);
        } else {
          backendStatus.value = 'error';
          backendError.value = error.message;
        }
      }
    };

    const showErrorDetails = () => {
      alert(`后端连接失败\n\n错误: ${backendError.value}\n\n请检查Python后端是否正常运行`);
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem('app-theme') || 'light';
      setTheme(savedTheme);

      checkBackendStatus();

      window.addEventListener('theme-changed', (e) => {
        if (e.detail && e.detail.theme) {
          theme.value = e.detail.theme;
        }
      });
      window.addEventListener('storage', (e) => {
        if (e.key === 'app-theme') {
          setTheme(e.newValue || 'light');
        }
      });
    });

    return {
      currentTab,
      tabs,
      currentComponent,
      switchTab,
      theme,
      setTheme,
      backendStatus,
      backendError,
      backendStatusClass,
      backendStatusText,
      showErrorDetails
    };
  }
};
</script>

<style>
#app {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ========== 侧边栏样式 ========== */
.sidebar {
  width: 280px;
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
  z-index: 100;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  border-right: 1px solid var(--border-color);
}

.sidebar-header {
  padding: 28px 24px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.logo-text h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.logo-text p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.nav-menu {
  padding: 16px 0;
  flex-grow: 1;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 24px;
  margin: 4px 12px;
  cursor: pointer;
  transition: var(--transition);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  position: relative;
  font-weight: 500;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--primary-color);
  border-radius: 0 3px 3px 0;
  transition: var(--transition);
}

.nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.nav-item:hover::before {
  height: 60%;
}

.nav-item.active {
  background: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
}

.nav-item.active::before {
  height: 80%;
}

.nav-icon {
  font-size: 1.3rem;
  width: 24px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  font-size: 0.95rem;
}

.sidebar-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.theme-toggle {
  display: flex;
  gap: 8px;
  background: var(--bg-tertiary);
  padding: 4px;
  border-radius: var(--radius-md);
}

.theme-btn {
  flex: 1;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
}

.theme-btn:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.theme-btn.active {
  background: var(--bg-primary);
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
  font-weight: 600;
}

.theme-icon {
  font-size: 1rem;
}

.theme-label {
  font-size: 0.8rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  transition: var(--transition);
}

.user-info:hover {
  background: var(--bg-secondary);
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: white;
  box-shadow: var(--shadow-md);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 2px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status {
  font-size: 0.75rem;
  color: var(--success-color);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status::before {
  content: '●';
  font-size: 0.6rem;
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  background: var(--bg-secondary);
  overflow-y: auto;
  transition: var(--transition);
  padding: 32px;
  margin-left: 280px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ========== 卡片样式 ========== */
.card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 36px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
  transition: var(--transition);
}


.card-title {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 0 0 28px 0;
  color: var(--text-primary);
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.card-title .icon {
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ========== 表单元素样式 ========== */
.input-group {
  margin-bottom: 24px;
}

.input-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95rem;
  letter-spacing: 0.2px;
}

.input-group input,
.input-group select,
.input-group textarea {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 1rem;
  transition: var(--transition);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: inherit;
}

.input-group select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 14px center;
  background-repeat: no-repeat;
  background-size: 18px;
  padding-right: 44px;
  cursor: pointer;
}

[data-theme="dark"] .input-group select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23cbd5e1' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
}

.input-group input:focus,
.input-group select:focus,
.input-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px var(--primary-light);
}

.input-group textarea {
  min-height: 150px;
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
}

/* ========== 按钮样式 ========== */
.btn {
  padding: 14px 28px;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
  letter-spacing: 0.3px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
  color: white;
  box-shadow: var(--shadow-md);
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--primary-hover), #7c3aed);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* ========== 结果区域 ========== */
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--border-color);
}

.result-title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.15rem;
  font-weight: 600;
}

.copy-btn {
  padding: 10px 18px;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.copy-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--border-hover);
  transform: translateY(-1px);
}

.result-content {
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 1.05rem;
  background: var(--bg-tertiary);
  padding: 24px;
  border-radius: var(--radius-md);
  border: 2px solid var(--border-color);
}

/* ========== 后端状态指示器 ========== */
.backend-status {
  margin-top: 16px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.ready .status-dot {
  background: #10b981;
}

.status-indicator.checking .status-dot {
  background: #f59e0b;
}

.status-indicator.error .status-dot {
  background: #ef4444;
}

.status-indicator.offline .status-dot {
  background: #6b7280;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

.error-details {
  margin-top: 8px;
}

.error-btn {
  padding: 6px 12px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.error-btn:hover {
  background: #dc2626;
}

/* ========== 加载动画 ========== */
.loading {
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.spinner {
  width: 22px;
  height: 22px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* ========== 响应式设计 ========== */
@media (max-width: 1024px) {
  .sidebar {
    width: 260px;
  }

  .main-content {
    margin-left: 260px;
    padding: 24px;
  }

  .card {
    padding: 28px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }

  .main-content {
    margin-left: 240px;
    padding: 20px;
  }

  .container {
    padding: 0;
  }

  .card {
    padding: 24px;
    margin-bottom: 20px;
  }

  .card-title {
    font-size: 1.4rem;
  }

  .theme-label {
    display: none;
  }
}

@media (max-width: 480px) {
  .sidebar {
    display: none;
  }

  .main-content {
    margin: 0;
    padding: 16px;
  }

  .card {
    padding: 20px;
  }

  .input-group input,
  .input-group select,
  .input-group textarea {
    padding: 12px 16px;
  }

  .btn {
    padding: 12px 20px;
    font-size: 0.95rem;
  }
}
</style>