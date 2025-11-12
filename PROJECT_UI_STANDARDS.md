# OmniMarket 金融监控系统 - 项目界面标准

## 概述
本文档定义了 OmniMarket 金融监控系统的统一界面设计标准和开发规范，确保所有页面具有一致的视觉风格和用户体验。

## 核心设计原则

### 1. 视觉主题
- **主背景**: `linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)`
- **容器背景**: `rgba(255, 255, 255, 0.1)` 带 `backdrop-filter: blur(10px)`
- **文字颜色**: 白色 `#ffffff`
- **强调色**: 
  - 绿色 (上涨/正面): `#00ff88`
  - 红色 (下跌/负面): `#ff4444`
  - 渐变强调: `linear-gradient(45deg, #00ff88, #00ccff)`

### 2. 导航键标准 (核心组件)

#### 布局规范
```css
.nav-bar {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: rgba(0, 0, 0, 0.98);
  min-height: 14px;
  backdrop-filter: blur(50px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  margin-bottom: 15px;
}
```

#### 按钮规范
```css
.nav-btn {
  font-size: 4.5px;
  min-height: 10px;
  line-height: 0.7;
  padding: 1px 2px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-family: 'Courier New', Monaco, Menlo, monospace;
  font-weight: 600;
  letter-spacing: 0.2px;
  text-transform: uppercase;
  transition: all 0.15s ease;
  border-right: 0.5px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
```

#### 交互状态
- **悬停效果**: `background: rgba(255, 255, 255, 0.05)` 和轻微上移
- **激活状态**: 绿色渐变背景和发光边框动画
- **颜色编码**: 绿色表示正面，红色表示负面

### 3. 字体规范
- **主字体**: `'Segoe UI', Tahoma, Geneva, Verdana, sans-serif`
- **金融数据字体**: `'Courier New', Monaco, Menlo, monospace` (等宽字体)
- **导航键字体大小**: `4.5px` (极小尺寸，专业紧凑)
- **标题字体大小**: `2.5em` (主标题)，`2em` (响应式)

### 4. 容器和布局
- **最大宽度**: `1200px`
- **圆角**: `15px` (主容器)，`8px` (卡片)
- **内边距**: `20px` (主容器)，`15px` (卡片)
- **阴影**: `0 8px 32px rgba(0, 0, 0, 0.3)`

## 已统一标准的页面

### ✅ 已完成统一导航键的页面

1. **KlineStyleDashboard** (`KlineStyleDashboard.css`)
   - 类名: `kline-nav-bar`, `kline-nav-btn`
   - 状态: 已完成 - 作为基准标准

2. **VirtualTradingPage** (`VirtualTradingPage.css`)
   - 类名: `virtual-trading-nav-bar`, `virtual-trading-nav-btn`
   - 状态: 已完成

3. **AlertsPage** (`AlertsPage.css`)
   - 类名: `alerts-nav-bar`, `alerts-nav-btn`
   - 状态: 已完成

4. **ChartPage** (`ChartPage.css`)
   - 类名: `chart-nav-bar`, `chart-nav-btn`
   - 状态: 已完成

5. **PortfolioPage** (`PortfolioPage.css`)
   - 类名: `portfolio-nav-bar`, `portfolio-nav-btn`
   - 状态: 已完成

6. **SettingsPage** (`SettingsPage.css`)
   - 类名: `settings-nav-bar`, `settings-nav-btn`
   - 状态: 已完成

7. **WarrantsMonitoringPage** (`WarrantsMonitoringPage.css`)
   - 类名: `warrants-nav-bar`, `warrants-nav-btn`
   - 状态: 已完成

8. **ProfessionalTradingDashboard** (`ProfessionalTradingDashboard.css`)
   - 类名: `professional-nav-bar`, `professional-nav-btn`
   - 状态: 已完成

9. **FinancialMonitoringSystem** (`FinancialMonitoringSystem.css`)
   - 类名: `financial-nav-bar`, `financial-nav-btn`
   - 状态: 已完成

## 响应式设计标准

### 移动端适配
```css
@media (max-width: 768px) {
  .nav-bar {
    grid-template-columns: repeat(4, 1fr);
    min-height: 12px;
  }
  
  .nav-btn {
    font-size: 3.5px;
    min-height: 8px;
  }
  
  .container {
    padding: 15px;
  }
}
```

### 小屏幕适配
```css
@media (max-width: 480px) {
  .market-info {
    grid-template-columns: 1fr;
  }
  
  .dashboard {
    padding: 10px;
  }
}
```

## 动画和交互标准

### 微交互效果
1. **悬停动画**: `transform: translateY(-0.5px)` 轻微上浮
2. **激活状态**: 底部发光线条动画 `pulse-glow`
3. **加载动画**: 旋转加载指示器
4. **状态指示**: 闪烁红点表示警报状态

### 动画定义
```css
@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

## 金融数据展示标准

### 价格卡片布局
```css
.market-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.info-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s ease;
}

.info-card:hover {
  transform: translateY(-2px);
}
```

### 数据格式
- **价格**: 使用等宽字体，精确到小数点后2-4位
- **涨跌幅**: 颜色编码 (绿色涨，红色跌)
- **状态指示器**: 实时连接状态显示

## 技术实现规范

### React + TypeScript
- 所有组件使用 TypeScript 严格类型
- 函数组件优先于类组件
- 使用 React Hooks 进行状态管理

### CSS 类命名约定
- 使用 BEM 命名法: `block__element--modifier`
- 页面特定前缀: `{page-name}-nav-bar`, `{page-name}-nav-btn`
- 状态类: `.active`, `.positive`, `.negative`

### 文件组织
- 每个页面独立的 CSS 文件
- 组件样式与页面样式分离
- 公共样式提取到共享文件

## 未来开发指南

### 新页面开发流程
1. 复制基准导航键样式到新页面的 CSS 文件
2. 更新类名为页面特定前缀
3. 确保响应式设计符合标准
4. 测试所有交互状态
5. 验证视觉一致性

### 样式修改流程
1. 先在基准文件 (`KlineStyleDashboard.css`) 测试修改
2. 确认效果后，同步到所有相关页面
3. 更新此文档记录变更

### 质量保证清单
- [ ] 导航键样式符合标准
- [ ] 颜色编码一致
- [ ] 响应式设计正常
- [ ] 交互效果流畅
- [ ] 字体使用正确
- [ ] 容器样式统一

## 版本历史

### v1.0 (2025-11-13)
- 初始标准定义
- 完成所有现有页面的导航键统一
- 建立响应式设计规范
- 定义金融数据展示标准

---

**维护者**: OmniMarket 开发团队  
**最后更新**: 2025-11-13  
**状态**: 活跃维护
