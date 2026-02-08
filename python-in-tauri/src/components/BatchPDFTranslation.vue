<template>
  <div class="batch-translation-container">
    <div class="under-construction">
      <div class="icon">🚧</div>
      <h2>功能维护中</h2>
      <p>PDF翻译功能正在进行升级维护，敬请期待...</p>
    </div>
  </div>
</template>

<script setup>
// 原有的逻辑暂停使用
</script>

<style scoped>
.batch-translation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  background-color: var(--bg-primary);
}

.under-construction {
  text-align: center;
  padding: 40px;
  background-color: var(--bg-secondary);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.icon {
  font-size: 48px;
  margin-bottom: 24px;
}

h2 {
  color: var(--text-primary);
  margin-bottom: 16px;
  font-size: 1.5rem;
}

p {
  color: var(--text-secondary);
  line-height: 1.6;
}
</style>