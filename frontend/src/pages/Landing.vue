<template>
  <div class="landing-page">
    <!-- 导航栏 -->
    <header>
      <div class="container">
        <nav>
          <div class="logo">
            <div class="logo-icon">N</div>
            <span>NEUSteel Agent</span>
          </div>
          <ul class="nav-links">
            <li><a href="#features">核心功能</a></li>
            <li><a href="#interactive">智能交互</a></li>
            <li><a href="#about">关于我们</a></li>
            <li><a @click="goToAuth" class="auth-link">登录/注册</a></li>
          </ul>
        </nav>
      </div>
    </header>

    <!-- 英雄区域 -->
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1>NEUSteel Agent</h1>
          <div class="tagline">钢铁智能，冶铸未来！</div>
          <p>NEUSteel Agent: Forging the Future of Metallurgy.</p>
          <p>东北大学冶金行业知识智能体，融合人工智能与行业专业知识，为冶金行业提供智能化解决方案。</p>
          <a @click="goToAuth" class="cta-button">开始使用</a>
        </div>
      </div>
    </section>

    <!-- 功能区域 -->
    <section class="features" id="features">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">⚙️</div>
            <h3>工艺优化</h3>
            <p>基于深度学习算法，分析冶金工艺参数，提供优化建议，提高生产效率和产品质量。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>数据分析</h3>
            <p>实时监控生产数据，智能识别异常模式，预测设备故障，降低维护成本。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔬</div>
            <h3>材料研发</h3>
            <p>利用材料科学知识库，辅助新材料研发，加速创新周期，提升研发效率。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>质量控制</h3>
            <p>智能质量检测系统，实时监控产品质量，确保符合行业标准和客户要求。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>智能决策</h3>
            <p>综合多维度数据，提供智能决策支持，优化生产计划和资源配置。</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔧</div>
            <h3>设备维护</h3>
            <p>预测性维护系统，提前识别设备问题，制定维护计划，延长设备寿命。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 交互区域 -->
    <section class="interactive" id="interactive">
      <div class="container">
        <h2 class="section-title">与NEUSteel Agent对话</h2>
        <div class="chat-container">
          <div class="chat-header">
            <div class="chat-icon">N</div>
            <span>NEUSteel Agent</span>
          </div>
          <div class="chat-preview">
            <div class="message-preview">
              <strong>您:</strong> 如何优化高炉炼铁工艺？
            </div>
            <div class="message-preview ai">
              <strong>NEUSteel Agent:</strong> 高炉炼铁工艺优化需要考虑多个关键因素...
            </div>
          </div>
          <div class="chat-cta">
            <a @click="goToAuth" class="cta-button">立即开始对话</a>
          </div>
        </div>
      </div>
    </section>

    <!-- 关于区域 -->
    <section class="about" id="about">
      <div class="container">
        <div class="about-content">
          <div class="about-text">
            <h2>关于NEUSteel Agent</h2>
            <p>NEUSteel Agent是东北大学基于人工智能技术开发的冶金行业专业知识智能体。它融合了东北大学在冶金领域的深厚学术积累与前沿人工智能技术，旨在为冶金行业提供智能化解决方案。</p>
            <p>我们的系统集成了大量冶金专业知识，包括钢铁冶炼、有色金属提取、材料科学等多个领域，能够为用户提供专业、准确的技术指导和决策支持。</p>
          </div>
          <div class="about-stats">
            <div class="stat-item">
              <div class="stat-number">1000+</div>
              <div class="stat-label">专业文档</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">50+</div>
              <div class="stat-label">工艺流程</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">24/7</div>
              <div class="stat-label">智能服务</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 联系区域 -->
    <section class="contact" id="contact">
      <div class="container">
        <h2 class="section-title">联系我们</h2>
        <div class="contact-content">
          <div class="contact-info">
            <h3>东北大学冶金学院</h3>
            <p>📍 辽宁省沈阳市和平区文化路3号巷11号</p>
            <p>📧 contact@neusteel.edu.cn</p>
            <p>📞 024-83687750</p>
          </div>
          <div class="contact-cta">
            <p>准备好开始您的智能冶金之旅了吗？</p>
            <a @click="goToAuth" class="cta-button">立即注册</a>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer>
      <div class="container">
        <div class="footer-content">
          <div class="footer-left">
            <div class="logo">
              <div class="logo-icon">N</div>
              <span>NEUSteel Agent</span>
            </div>
            <p>钢铁智能，冶铸未来</p>
          </div>
          <div class="footer-right">
            <p>&copy; 2024 东北大学冶金学院. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToAuth = () => {
  router.push('/auth')
}
</script>

<style scoped>
/* 基础样式 */
:root {
  --primary-color: #1a365d; /* 深蓝钢色 */
  --secondary-color: #c53030; /* 炽热红色 */
  --accent-color: #d69e2e; /* 金色 */
  --light-color: #f7fafc;
  --dark-color: #2d3748;
  --gray-color: #a0aec0;
  --steel-gradient: linear-gradient(135deg, #4a5568, #2d3748);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

.landing-page {
  background-color: #f5f7fa;
  color: var(--dark-color);
  line-height: 1.6;
}

.container {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

/* 导航栏 */
header {
  background: var(--steel-gradient);
  color: white;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--accent-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
}

.nav-links {
  display: flex;
  list-style: none;
}

.nav-links li {
  margin-left: 2rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-links a:hover {
  color: var(--accent-color);
}

.auth-link {
  background: var(--accent-color);
  padding: 8px 16px;
  border-radius: 20px;
  color: var(--dark-color) !important;
  font-weight: bold;
}

.auth-link:hover {
  background: #e2b93e;
  color: var(--dark-color) !important;
}

/* 英雄区域 */
.hero {
  background: var(--steel-gradient);
  color: white;
  padding: 5rem 0;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.05)"/></svg>');
  background-size: cover;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.tagline {
  color: var(--accent-color);
  font-weight: bold;
  font-size: 1.8rem;
  margin: 1rem 0;
}

.cta-button {
  display: inline-block;
  background: var(--secondary-color);
  color: white;
  padding: 12px 30px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s, transform 0.3s;
  margin-top: 1rem;
  cursor: pointer;
}

.cta-button:hover {
  background: #b91c1c;
  transform: translateY(-3px);
}

/* 功能区域 */
.features {
  padding: 5rem 0;
  background-color: white;
}

.section-title {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.2rem;
  color: var(--primary-color);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--light-color);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  color: white;
  font-size: 1.5rem;
}

.feature-card h3 {
  color: var(--primary-color);
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.feature-card p {
  color: var(--gray-color);
  line-height: 1.6;
}

/* 交互区域 */
.interactive {
  padding: 5rem 0;
  background: var(--light-color);
}

.chat-container {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  overflow: hidden;
}

.chat-header {
  background: var(--steel-gradient);
  color: white;
  padding: 1rem;
  display: flex;
  align-items: center;
  font-weight: bold;
}

.chat-icon {
  width: 30px;
  height: 30px;
  background: var(--accent-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  color: var(--dark-color);
  font-weight: bold;
}

.chat-preview {
  padding: 2rem;
}

.message-preview {
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
}

.message-preview.ai {
  background: var(--primary-color);
  color: white;
}

.chat-cta {
  padding: 1rem 2rem 2rem;
  text-align: center;
}

/* 关于区域 */
.about {
  padding: 5rem 0;
  background: white;
}

.about-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 3rem;
  align-items: center;
}

.about-text h2 {
  color: var(--primary-color);
  margin-bottom: 1.5rem;
  font-size: 2rem;
}

.about-text p {
  color: var(--gray-color);
  margin-bottom: 1rem;
  line-height: 1.7;
}

.about-stats {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--light-color);
  border-radius: 8px;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--gray-color);
  font-weight: 500;
}

/* 联系区域 */
.contact {
  padding: 5rem 0;
  background: var(--light-color);
}

.contact-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.contact-info h3 {
  color: var(--primary-color);
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.contact-info p {
  color: var(--gray-color);
  margin-bottom: 0.5rem;
}

.contact-cta {
  text-align: center;
}

.contact-cta p {
  color: var(--dark-color);
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

/* 页脚 */
footer {
  background: var(--steel-gradient);
  color: white;
  padding: 2rem 0;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left .logo {
  margin-bottom: 0.5rem;
}

.footer-left p {
  color: var(--gray-color);
  font-style: italic;
}

.footer-right p {
  color: var(--gray-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }

  .tagline {
    font-size: 1.4rem;
  }

  .hero p {
    font-size: 1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .about-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .about-stats {
    flex-direction: row;
    justify-content: space-around;
  }

  .contact-content {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .nav-links {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links li {
    margin-left: 0;
  }

  nav {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }

  .hero {
    padding: 3rem 0;
  }

  .features, .interactive, .about, .contact {
    padding: 3rem 0;
  }

  .section-title {
    font-size: 1.8rem;
  }
}
</style>
