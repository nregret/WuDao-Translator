<template>
  <div class="batch-text-replace">
    <div class="main-container">

      <!-- 左侧：文件管理区域 -->
      <div class="left-panel">
        <div class="panel-header">
          <h3>
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            文件列表
          </h3>
          <span class="file-count" v-if="selectedFiles.length > 0">{{ selectedFiles.length }} 个文件</span>
        </div>

        <div class="file-list-container">
          <div v-if="selectedFiles.length === 0" class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <p>暂无文件，请添加</p>
          </div>

          <div v-else class="file-list">
            <div class="file-item" v-for="(file, index) in selectedFiles" :key="index">
              <div class="file-name" :title="file">{{ file }}</div>
              <button @click.stop="removeFile(index)" class="remove-btn" title="移除文件">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                  stroke-linejoin="round">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="panel-footer">
          <div class="action-buttons">
            <button @click="selectFiles" class="action-btn">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5v14M5 12h14" />
              </svg>
              添加文件
            </button>
            <button @click="selectFolder" class="action-btn">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
              </svg>
              添加文件夹
            </button>
            <button @click="clearFiles" class="action-btn danger" v-if="selectedFiles.length > 0">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
              </svg>
              清空
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：规则与执行区域 -->
      <div class="right-panel">
        <div class="panel-header">
          <h3>
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8v12M17 20l-4-4M17 20l4-4" />
            </svg>
            替换规则
          </h3>
          <button @click="addRule" class="add-rule-btn-header" title="添加规则">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
            添加规则
          </button>
        </div>

        <div class="rules-container">
          <div class="rules-list">
            <div v-for="(rule, index) in rules" :key="index" class="rule-item">
              <div class="rule-content">
                <div class="rule-index">#{{ index + 1 }}</div>
                <input v-model="rule.searchText" placeholder="查找内容" class="rule-input search-input" />
                <div class="arrow-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
                <input v-model="rule.replaceText" placeholder="替换为" class="rule-input replace-input" />
                <button @click="removeRule(index)" class="remove-rule-btn" v-if="rules.length > 1 || rules.length === 1"
                  title="删除此规则">
                  <!-- Always show delete button or handle visibility via CSS to keep alignment? 
                        Actually keeping visibility logic is fine, but maybe user wants button to occupy space? 
                        The previous code 'v-if="rules.length > 1"' meant the first rule has no delete button, 
                        which might make the right edge misaligned compared to other rows if they exist.
                        Let's change: Always show the button but disable it if length == 1? 
                        Or just allow deleting the only rule (which clears it)?
                        The logic 'removeRule' currently splices. 
                        Let's stick to v-if but maybe use visibility: hidden for layout stability? 
                        Actually, let's just leave it as is, but if the user has 1 rule, no button. 
                        If 2 rules, both have buttons. 
                        Wait, if I have 2 rules, and I delete one, the remaining one loses the button?
                        Yes, that's standard. 
                        But maybe misalignment comes from the fact that inputs stretch differently if button is missing?
                        Ah! If button is missing, 'flex: 1' inputs will grow to fill that space, making the input widths different from rows WITH buttons!
                        This is likely the "misalignment" if the user has multiple rules but noticed the first one changed? 
                        Wait, if multiple rules, ALL have buttons.
                        Except if I verify logic: `v-if="rules.length > 1"`.
                        So if I have 2 rules: both have buttons. widths are equal.
                        If I have 1 rule: no button. widths expand.
                        This is acceptable.
                        
                        However, the user says "单个规则的UI" (single rule UI). 
                        It might imply the vertical alignment of elements WITHIN the row.
                        
                        I will stick to flattening and height enforcement first.
                   -->
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-footer settings-footer">
          <div class="save-options">
            <div class="option-row">
              <label class="radio-label">
                <input type="radio" v-model="saveMode" value="replace" />
                <span>覆盖原文件</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="saveMode" value="save_as" />
                <span>另存为新文件</span>
              </label>
            </div>

            <div class="path-selector" v-if="saveMode === 'save_as'">
              <div class="path-display" :title="savePath">{{ savePath || '请选择保存路径...' }}</div>
              <button @click="selectSavePath" class="path-btn">选择</button>
            </div>
          </div>

          <button @click="startReplace" class="execute-btn"
            :disabled="isReplacing || selectedFiles.length === 0 || !hasValidRules || (saveMode === 'save_as' && !savePath)"
            :class="{ 'processing': isReplacing }">
            <span v-if="!isReplacing">开始批量替换</span>
            <span v-else>
              <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              正在处理 {{ replaceProgress.current }}/{{ replaceProgress.total }}
            </span>
            <div class="progress-bar" :style="{ width: replaceProgress.percent + '%' }"></div>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { invoke } from '@tauri-apps/api/core';

export default {
  name: 'BatchTextReplace',
  setup() {
    // 替换规则列表
    const rules = ref([
      { searchText: '', replaceText: '' }
    ]);

    // 文件选择
    const selectedFiles = ref([]);
    const saveMode = ref('replace');
    const savePath = ref('');

    // 替换状态
    const isReplacing = ref(false);
    const replaceProgress = ref({
      current: 0,
      total: 0,
      percent: 0
    });

    // 计算是否有有效规则
    const hasValidRules = computed(() => {
      return rules.value.some(rule => rule.searchText.trim() !== '');
    });

    // 添加新规则
    const addRule = () => {
      rules.value.push({ searchText: '', replaceText: '' });
      // 滚动到底部
      setTimeout(() => {
        const container = document.querySelector('.rules-container');
        if (container) container.scrollTop = container.scrollHeight;
      }, 50);
    };

    // 删除规则
    const removeRule = (index) => {
      if (rules.value.length > 1) {
        rules.value.splice(index, 1);
      }
    };

    // 选择文件
    const selectFiles = async () => {
      try {
        const { open } = await import('@tauri-apps/plugin-dialog');

        const result = await open({
          multiple: true,
          filters: [{ name: 'Text Files', extensions: ['txt', 'md', 'json', 'js', 'html', 'css', 'py', 'rs'] }] // 扩展一些常见文本格式
        });

        if (result) {
          let paths = [];

          if (Array.isArray(result)) {
            paths = result.map(f => typeof f === 'string' ? f : f.path || f.name);
          } else {
            const path = typeof result === 'string' ? result : result.path || result.name;
            if (path) {
              paths = [path];
            }
          }

          for (const path of paths) {
            if (!selectedFiles.value.includes(path)) {
              selectedFiles.value.push(path);
            }
          }
        }
      } catch (error) {
        console.error('选择文件失败:', error);
        alert('选择文件失败: ' + error.message);
      }
    };

    // 选择文件夹
    const selectFolder = async () => {
      try {
        const { open } = await import('@tauri-apps/plugin-dialog');

        const folderResult = await open({
          directory: true,
          multiple: false
        });

        if (folderResult) {
          const folderPath = typeof folderResult === 'string' ? folderResult : folderResult.path || folderResult.name;
          if (folderPath) {
            try {
              const files = await invoke('scan_folder_txt_files', { folderPath });
              if (files && Array.isArray(files) && files.length > 0) {
                selectedFiles.value = [...new Set([...selectedFiles.value, ...files])];
              } else {
                alert('该文件夹中没有找到文本文件');
              }
            } catch (error) {
              console.error('扫描文件夹失败:', error);
              alert(`扫描文件夹失败: ${error.message}`);
            }
          }
        }
      } catch (error) {
        console.error('选择文件夹失败:', error);
        alert('选择文件夹失败: ' + error.message);
      }
    };

    // 选择保存路径
    const selectSavePath = async () => {
      try {
        const { open } = await import('@tauri-apps/plugin-dialog');

        const result = await open({
          directory: true,
          multiple: false
        });

        if (result) {
          const path = typeof result === 'string' ? result : result.path || result.name;
          if (path) {
            savePath.value = path;
          }
        }
      } catch (error) {
        console.error('选择保存路径失败:', error);
      }
    };

    // 移除文件
    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1);
    };

    // 清空文件
    const clearFiles = () => {
      selectedFiles.value = [];
    };

    // 开始批量替换
    const startReplace = async () => {
      if (selectedFiles.value.length === 0) {
        alert('请先选择文件');
        return;
      }

      if (!hasValidRules.value) {
        alert('请至少填写一条有效的替换规则');
        return;
      }

      if (saveMode.value === 'save_as' && !savePath.value) {
        alert('请选择保存路径');
        return;
      }

      isReplacing.value = true;
      const totalFiles = selectedFiles.value.length;
      let successCount = 0;
      let failCount = 0;

      // 初始化进度
      replaceProgress.value = {
        current: 0,
        total: totalFiles,
        percent: 0
      };

      try {
        // 过滤有效规则
        const validRules = rules.value.filter(rule => rule.searchText.trim() !== '');

        // 逐个文件处理，以便实时更新进度
        for (let i = 0; i < selectedFiles.value.length; i++) {
          const filePath = selectedFiles.value[i];

          try {
            // 读取文件内容
            const fileContent = await invoke('read_file_content', { filePath });

            if (!fileContent && fileContent !== '') { // 允许空文件
              console.warn(`File empty or read failed: ${filePath}`);
              failCount++;
              continue;
            }

            // 应用所有替换规则
            let newContent = fileContent;
            for (const rule of validRules) {
              if (rule.searchText) {
                // 使用全局替换，不仅仅是第一个
                const regex = new RegExp(rule.searchText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                newContent = newContent.replace(regex, rule.replaceText || '');
              }
            }

            // 保存替换后的文件
            let finalSavePath;
            if (saveMode.value === 'replace') {
              finalSavePath = filePath;
            } else {
              // 处理文件名
              const pathParts = filePath.split(/[/\\]/);
              const fileName = pathParts.pop();

              // 简单处理文件名，插入_replaced
              const lastDotIndex = fileName.lastIndexOf('.');
              let newFileName;
              if (lastDotIndex > 0) {
                newFileName = fileName.substring(0, lastDotIndex) + '_replaced' + fileName.substring(lastDotIndex);
              } else {
                newFileName = fileName + '_replaced';
              }

              finalSavePath = await invoke('join_path', {
                dir: savePath.value,
                file: newFileName
              });
            }

            await invoke('write_file_content', {
              filePath: finalSavePath,
              content: newContent
            });

            successCount++;
          } catch (error) {
            console.error(`替换文件 ${filePath} 失败:`, error);
            failCount++;
          }

          // 实时更新进度
          replaceProgress.value = {
            current: i + 1,
            total: totalFiles,
            percent: Math.round(((i + 1) / totalFiles) * 100)
          };
        }

        // 替换完成，等待一段后重置
        setTimeout(() => {
          replaceProgress.value = {
            current: 0,
            total: 0,
            percent: 0
          };
          isReplacing.value = false;
          alert(`替换完成！成功: ${successCount}，失败: ${failCount}`);
        }, 500);

      } catch (error) {
        console.error('批量替换错误:', error);
        alert(`替换失败: ${error.message}`);
        isReplacing.value = false;
      }
    };

    return {
      rules,
      selectedFiles,
      saveMode,
      savePath,
      isReplacing,
      replaceProgress,
      hasValidRules,
      addRule,
      removeRule,
      selectFiles,
      selectFolder,
      selectSavePath,
      removeFile,
      clearFiles,
      startReplace
    };
  }
};
</script>

<style scoped>
.batch-text-replace {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.main-container {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

/* 通用面板样式 */
.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.left-panel {
  width: 300px;
  border-right: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  background-color: var(--bg-primary);
  min-width: 0;
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  flex-shrink: 0;
  background-color: var(--bg-tertiary);
}

.panel-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-header .icon {
  width: 18px;
  height: 18px;
  color: var(--primary-color);
}

.panel-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  flex-shrink: 0;
}

/* 左侧：文件列表样式 */
.file-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.file-count {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  padding: 2px 8px;
  border-radius: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-tertiary);
  gap: 12px;
  opacity: 0.6;
}

.empty-icon {
  width: 48px;
  height: 48px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.file-item:hover {
  border-color: var(--primary-light);
  transform: translateX(2px);
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background-color: var(--error-bg);
  color: var(--error-color);
}

.remove-btn svg {
  width: 14px;
  height: 14px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  background-color: var(--bg-tertiary);
}

.action-btn.danger:hover {
  border-color: var(--error-color);
  color: var(--error-color);
}

.action-btn .btn-icon {
  width: 16px;
  height: 16px;
}

/* 右侧：规则列表样式 */
.rules-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.add-rule-btn-header {
  padding: 6px 12px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.add-rule-btn-header:hover {
  background-color: var(--primary-hover);
}

.add-rule-btn-header .btn-icon {
  width: 16px;
  height: 16px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Simplified compact rule item */
.rule-item {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px;
  transition: border-color 0.2s;
}

.rule-item:hover {
  border-color: var(--border-hover);
}

.rule-content {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  /* Enforce row height */
}

.rule-index {
  font-weight: 700;
  color: var(--text-tertiary);
  font-size: 0.85rem;
  width: 24px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Remove .input-group style */

.rule-input {
  flex: 1;
  /* Make inputs grow */
  width: 0;
  /* Important for flex growth */
  padding: 0 10px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.85rem;
  height: 32px;
  line-height: 30px;
  /* Ensure text matches height */
}

.rule-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-light);
}

.replace-input {
  background-color: var(--bg-tertiary);
}

.arrow-icon {
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 24px;
  height: 32px;
}

.arrow-icon svg {
  width: 16px;
  height: 16px;
}

.remove-rule-btn {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.remove-rule-btn:hover {
  color: var(--error-color);
  background-color: var(--error-bg);
}

.remove-rule-btn svg {
  width: 16px;
  height: 16px;
}


/* 底部操作区 */
.settings-footer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.save-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-row {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.path-selector {
  display: flex;
  gap: 10px;
}

.path-display {
  flex: 1;
  padding: 8px 12px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.path-btn {
  padding: 8px 16px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

.path-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.execute-btn {
  width: 100%;
  padding: 14px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: background-color 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.execute-btn:disabled {
  background-color: var(--disabled-bg);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.execute-btn.processing {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--primary-color);
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 4px;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.spinner {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
    overflow-y: auto;
  }

  .left-panel {
    width: 100%;
    height: 300px;
    /* 固定高度或者比例 */
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .right-panel {
    height: auto;
    flex: 1;
    min-height: 400px;
  }
}
</style>
