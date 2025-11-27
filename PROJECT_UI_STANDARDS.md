# OmniMarket 金融监控系统 - 项目界面标准

## 概述
本文档定义了 OmniMarket 金融监控系统的统一界面设计标准和开发规范，确保所有页面具有一致的视觉风格和用户体验。**所有新界面开发必须遵循彭博终端风格标准**，提供专业金融软件的视觉体验。

## 彭博终端风格标准

### 1. 核心视觉主题
- **主背景**: `#0a0e17` (深蓝黑色，专业金融终端背景)
- **次级背景**: `#141a2a` (深色容器背景)
- **边框颜色**: `#2a3a5a` (深蓝色边框)
- **文字颜色**: 
  - 主文字: `#e0e0e0` (浅灰色)
  - 次要文字: `#a0a0a0` (中灰色)
  - 强调文字: `#ffffff` (白色)
- **状态颜色**:
  - 上涨/正面: `#00ff88` (亮绿色)
  - 下跌/负面: `#ff4444` (亮红色)
  - 中性/信息: `#00ccff` (亮蓝色)
  - 警告: `#ffaa00` (琥珀色)

### 2. 布局和信息密度
- **紧凑网格布局**: 使用CSS Grid实现高信息密度
- **最小边距**: `2px` 到 `5px` 之间
- **面板间距**: `8px` 到 `12px`
- **字体大小**: 
  - 数据字体: `12px` 到 `14px` (等宽字体)
  - 标签字体: `10px` 到 `12px`
  - 标题字体: `16px` 到 `18px`

### 3. 金融数据展示标准
#### 价格卡片规范
```css
.price-card {
  background: #141a2a;
  border: 1px solid #2a3a5a;
  border-radius: 4px;
  padding: 8px 12px;
  font-family: 'Courier New', Monaco, Menlo, monospace;
  font-size: 13px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px;
  min-height: 40px;
}

.price-positive {
  color: #00ff88;
  font-weight: bold;
}

.price-negative {
  color: #ff4444;
  font-weight: bold;
}
```

#### K线图表区域
- 使用深色主题的ECharts或Lightweight Charts
- 图表背景: `#0a0e17`
- 网格线: `#1a243a`
- 坐标轴: `#4a5a7a`

### 4. 控制面板规范
```css
.control-panel {
  background: #141a2a;
  border: 1px solid #2a3a5a;
  border-radius: 4px;
  padding: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.control-button {
  background: #2a3a5a;
  border: 1px solid #3a4a6a;
  color: #e0e0e0;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-button:hover {
  background: #3a4a7a;
  border-color: #4a5a8a;
}

.control-button:active {
  background: #1a2a4a;
}
```

## 核心设计原则

### 1. 视觉主题
- **主背景**: `#0a0e17` (彭博终端风格深色主题)
- **容器背景**: `#141a2a` 带轻微透明度
- **文字颜色**: `#e0e0e0` (主文字)，`#a0a0a0` (次要文字)
- **强调色**: 
  - 绿色 (上涨/正面): `#00ff88`
  - 红色 (下跌/负面): `#ff4444`
  - 蓝色 (信息/中性): `#00ccff`

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

10. **AutoTradingPage** (`AutoTradingPage.css`)
    - 类名: 使用标准按钮样式，无特定导航键
    - 状态: 已完成 - 彭博终端风格改造
    - 特色: 全自动交易系统专用界面，包含策略选择、风险控制、紧急熔断等功能

11. **SemiAutoTradingPage** (`SemiAutoTradingPage.css`)
    - 类名: `semi-auto-trading-nav-bar`, `semi-auto-trading-nav-btn`
    - 状态: 已完成 - 彭博终端风格改造
    - 特色: 半自动交易系统专用界面，包含信号生成、交易验证、人工确认执行等功能

### 全自动交易系统专用标准

#### 控制面板布局
```css
.main-content {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 15px;
}
```

#### 交易控制按钮
```css
.btn-start { background: #1a3a2a; color: #00ff88; border: 1px solid #00ff88; }
.btn-stop { background: #3a1a1a; color: #ff4444; border: 1px solid #ff4444; }
.btn-pause { background: #3a3a1a; color: #ffaa00; border: 1px solid #ffaa00; }
.btn-resume { background: #1a2a3a; color: #00ccff; border: 1px solid #00ccff; }
.btn-emergency { background: #3a1a2a; color: #ff0066; border: 1px solid #ff0066; }
```

#### 风险等级颜色编码
```css
.risk-低风险 { background: #1a3a2a; color: #00ff88; }
.risk-中等风险 { background: #3a3a1a; color: #ffaa00; }
.risk-高风险 { background: #3a1a1a; color: #ff4444; }
.risk-极高风险 { background: #3a1a2a; color: #ff0066; }
```

#### 状态指示器
```css
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
```

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
