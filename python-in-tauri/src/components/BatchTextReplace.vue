<template>
  <div class="batch-text-replace">
    <div class="card" :class="{ 'replacing': isReplacing || replaceProgress.total > 0 }" :style="progressBorderStyle">
      <h2 class="card-title">
        <div class="title-content">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8v12M17 20l-4-4M17 20l4-4"/>
          </svg>
          批量文本替换
        </div>
        <button @click="addRule" class="add-rule-btn small" title="添加规则">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
        </button>
      </h2>
      
      <!-- 替换规则区域 - 支持多条规则 -->
      <div class="replace-rules-section">
        <div class="rules-container">
          <div class="rules-list">
            <div 
              v-for="(rule, index) in rules" 
              :key="index" 
              class="rule-item"
            >
              <div class="rule-number">{{ index + 1 }}</div>
              <div class="rule-inputs">
                <input 
                  v-model="rule.searchText" 
                  placeholder="被替换内容"
                  class="rule-input search-input"
                />
                <input 
                  v-model="rule.replaceText" 
                  placeholder="替换为"
                  class="rule-input replace-input"
                />
              </div>
              <button @click="removeRule(index)" class="remove-rule-btn" v-if="rules.length > 1" title="删除此规则">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 文件上传区域 -->
      <div class="file-upload-section">
        <div class="upload-buttons">
          <button @click="selectFiles" class="upload-btn file-btn">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <span class="btn-text">选择文件</span>
          </button>
          <button @click="selectFolder" class="upload-btn folder-btn">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="btn-text">选择文件夹</span>
          </button>
        </div>
        
        <div v-if="selectedFiles.length > 0" class="file-list-content">
          <div class="file-list-header">
            <span class="file-count-text">已选择 {{ selectedFiles.length }} 个文件</span>
            <button @click="clearFiles" class="clear-btn">清空</button>
          </div>
          <div class="file-list">
            <div class="file-item" v-for="(file, index) in selectedFiles" :key="index">
              <span class="file-name">{{ file }}</span>
              <button @click.stop="removeFile(index)" class="remove-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 保存选项 -->
      <div class="save-options">
        <div class="option-group">
          <label class="radio-option">
            <input 
              type="radio" 
              v-model="saveMode" 
              value="replace"
            />
            <span>替换原文件</span>
          </label>
          <label class="radio-option">
            <input 
              type="radio" 
              v-model="saveMode" 
              value="save_as"
            />
            <span>另存为新文件</span>
          </label>
        </div>
        
        <div class="save-path-selector" :class="{ disabled: saveMode === 'replace' }">
          <label class="path-label">保存路径：</label>
          <div class="path-display">{{ savePath || '未选择' }}</div>
          <button 
            @click="selectSavePath" 
            class="btn btn-secondary small"
            :disabled="saveMode === 'replace'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            选择文件夹
          </button>
        </div>
      </div>
      
      <!-- 执行按钮 -->
      <div class="replace-action">
        <button 
          @click="startReplace" 
          class="btn btn-primary"
          :disabled="selectedFiles.length === 0 || !hasValidRules || isReplacing || (saveMode === 'save_as' && !savePath)"
        >
          <svg v-if="!isReplacing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
            <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
            <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
            <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
          </svg>
          <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          {{ isReplacing ? '替换中...' : '开始替换' }}
        </button>
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
    
    // 计算进度条边框样式
    const progressBorderStyle = computed(() => {
      if (replaceProgress.value.total > 0) {
        const percent = replaceProgress.value.percent;
        return {
          '--progress-percent': `${percent}%`
        };
      }
      return {};
    });
    
    // 添加新规则
    const addRule = () => {
      rules.value.push({ searchText: '', replaceText: '' });
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
          filters: [{ name: 'Text Files', extensions: ['txt'] }]
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
            if (path.toLowerCase().endsWith('.txt')) {
              if (!selectedFiles.value.includes(path)) {
                selectedFiles.value.push(path);
              }
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
                alert('该文件夹中没有找到 .txt 文件');
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
            
            if (!fileContent || !fileContent.trim()) {
              failCount++;
              continue;
            }
            
            // 应用所有替换规则
            let newContent = fileContent;
            for (const rule of validRules) {
              if (rule.searchText && rule.searchText.trim()) {
                newContent = newContent.split(rule.searchText).join(rule.replaceText || '');
              }
            }
            
            // 保存替换后的文件
            let finalSavePath;
            if (saveMode.value === 'replace') {
              finalSavePath = filePath;
            } else {
              const fileName = filePath.split(/[/\\]/).pop();
              const name = fileName.replace(/\.txt$/, '');
              const newFileName = `${name}_replaced.txt`;
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
        
        // 替换完成，等待3秒后重置
        setTimeout(() => {
          replaceProgress.value = {
            current: 0,
            total: 0,
            percent: 0
          };
        }, 3000);
        
        alert(`替换完成！成功: ${successCount}，失败: ${failCount}`);
      } catch (error) {
        console.error('批量替换错误:', error);
        alert(`替换失败: ${error.message}`);
      } finally {
        isReplacing.value = false;
      }
    };
    
    // 加载保存的规则
    onMounted(() => {
    });
    
    return {
      rules,
      selectedFiles,
      saveMode,
      savePath,
      isReplacing,
      replaceProgress,
      hasValidRules,
      progressBorderStyle,
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
  display: flex;
  flex-direction: column;
  gap: 0;
  height: 100%;
  min-height: 0;
}

.card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  flex: 1;
  overflow: hidden;
  position: relative;
  border-bottom: 4px solid var(--border-color);
}

.card.replacing::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 4px;
  width: var(--progress-percent, 0%);
  background: var(--primary-color);
  transition: width 0.3s ease;
  z-index: 1;
}

.card-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
}

.card-title .title-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title .icon {
  width: 24px;
  height: 24px;
  color: var(--primary-color);
}

/* ========== 替换规则区域 ========== */
.replace-rules-section {
  margin-bottom: 20px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rules-container {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  padding: 16px;
  transition: all 0.2s ease;
}

.rules-container:hover {
  border-color: var(--border-hover);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.rules-container::-webkit-scrollbar {
  width: 8px;
}

.rules-container::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

.rules-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
  transition: background var(--transition-fast);
}

.rules-container::-webkit-scrollbar-thumb:hover {
  background: var(--border-hover);
}

.rules-container::-moz-scrollbar {
  width: 8px;
}

.rules-container::-moz-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

.rules-container::-moz-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
  transition: background var(--transition-fast);
}

.rules-container::-moz-scrollbar-thumb:hover {
  background: var(--border-hover);
}

.add-rule-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.add-rule-btn.small {
  padding: 8px 12px;
  min-width: 40px;
  height: 40px;
}

.add-rule-btn.small .btn-icon {
  width: 20px;
  height: 20px;
}

.add-rule-btn.small .btn-text {
  display: none;
}

.add-rule-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.add-rule-btn:active {
  transform: translateY(0);
}

.add-rule-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.rule-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.rule-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  background: transparent;
  color: var(--text-primary);
  border-radius: 0;
  font-weight: 600;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.rule-inputs {
  flex: 1;
  display: flex;
  gap: 8px;
}

.rule-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: inherit;
  height: 36px;
  transition: all 0.2s ease;
}

.rule-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
  background-color: var(--bg-primary);
}

.rule-input:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: -2px;
}

.rule-input::placeholder {
  color: var(--text-tertiary);
}

.remove-rule-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  opacity: 0.6;
  transition: all 0.2s ease;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-rule-btn svg {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
}

.remove-rule-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.remove-rule-btn:hover svg {
  color: var(--error-color);
}

.remove-rule-btn:active {
  transform: scale(0.95);
}

.remove-rule-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  border-radius: 4px;
}

/* ========== 文件上传区域 ========== */
.file-upload-section {
  margin-bottom: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.upload-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.upload-btn {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  min-height: 48px;
}

.upload-btn:hover {
  border-color: var(--primary-color);
  background: var(--bg-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
}

.upload-btn:active {
  transform: translateY(0);
}

.upload-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.upload-btn .btn-icon {
  width: 20px;
  height: 20px;
  opacity: 0.8;
  flex-shrink: 0;
}

.upload-btn .btn-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

.file-list-content {
  border: 2px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  transition: all 0.2s ease;
}

.file-list-content:hover {
  border-color: var(--border-hover);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.file-count-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
  transform: translateX(2px);
}

.file-name {
  font-size: 0.85rem;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

.remove-btn:hover {
  color: var(--error-color);
  transform: scale(1.1);
}

.remove-btn:active {
  transform: scale(0.95);
}

.remove-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  border-radius: 4px;
}

.clear-btn {
  background: var(--error-color) !important;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: 6px 16px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #dc2626 !important;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.clear-btn:active {
  transform: scale(0.95);
}

.clear-btn:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* ========== 保存选项 ========== */
.save-options {
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 2px solid var(--border-color);
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.save-options:hover {
  border-color: var(--border-hover);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.option-group {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.radio-option:hover {
  background: var(--bg-tertiary);
}

.radio-option input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--primary-color);
  transition: transform 0.2s ease;
}

.radio-option input[type="radio"]:hover {
  transform: scale(1.1);
}

.save-path-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  transition: opacity 0.2s ease;
}

.save-path-selector.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.save-path-selector.disabled .path-display {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.save-path-selector.disabled .btn {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-path-selector.disabled .path-label {
  color: var(--text-secondary);
}

.path-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.path-display {
  flex: 1;
  padding: 10px 14px;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.path-display:hover {
  border-color: var(--border-hover);
}

.path-display:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-light);
}

/* ========== 执行按钮 ========== */
.replace-action {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transform: translateY(-1px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:focus-visible:not(:disabled) {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn:disabled svg {
  opacity: 0.6;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-primary);
  border-color: var(--border-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-secondary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-secondary:focus-visible:not(:disabled) {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.btn.small {
  padding: 8px 16px;
  font-size: 0.8rem;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .card-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-title .title-content {
    width: 100%;
  }
  
  .add-rule-btn.small {
    width: 100%;
    min-width: auto;
    height: auto;
    padding: 10px 16px;
  }
  
  .add-rule-btn.small .btn-text {
    display: inline;
  }
  
  .rules-container {
    max-height: 300px;
    padding: 12px;
  }
  
  .rules-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .rule-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 16px;
  }
  
  .rule-number {
    width: 100%;
    justify-content: center;
  }
  
  .rule-inputs {
    width: 100%;
    flex-direction: column;
    gap: 12px;
  }
  
  .rule-input {
    width: 100%;
  }
  
  .remove-rule-btn {
    position: static;
    align-self: flex-end;
  }
  
  .option-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .save-path-selector {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .upload-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .upload-btn {
    width: 100%;
    justify-content: center;
  }
  
  .rule-actions {
    flex-direction: column;
  }
  
  .card-title {
    font-size: 0.9rem;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .file-list-content {
    padding: 16px;
  }
  
  .file-item {
    padding: 10px 12px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .rules-container {
    max-height: 350px;
  }
  
  .rule-inputs {
    gap: 6px;
  }
  
  .upload-buttons {
    gap: 8px;
  }
  
  .file-list-content {
    padding: 18px;
  }
}

@media (min-width: 1025px) {
  .card {
    max-width: 100%;
  }
  
  .rules-container {
    max-height: 400px;
  }
}
</style>
