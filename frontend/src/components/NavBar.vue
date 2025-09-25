<template>
  <nav class="nav">
    <div class="wrap">
      <div class="brand">Knowledge Horizon</div>
      <div class="links">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/auth">登录</RouterLink>
      </div>
    </div>
  </nav>
</template>

<script setup>
</script>

<style scoped>
.nav { border-bottom: 1px solid #eee; }
.wrap { max-width: 960px; margin: 0 auto; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; }
.brand { font-weight: 600; }
.links a { margin-left: 12px; }
</style>
