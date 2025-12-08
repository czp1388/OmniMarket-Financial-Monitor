import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom right, #0a0e17, #0d1219, #0a0e17)',
      color: 'white',
      padding: '40px',
      fontFamily: 'sans-serif'
    }}>
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        background: 'rgba(20, 26, 42, 0.8)',
        border: '1px solid #2a3a5a',
        borderRadius: '16px',
        padding: '40px'
      }}>
        <h1 style={{
          fontSize: '36px',
          marginBottom: '20px',
          background: 'linear-gradient(to right, #00ccff, #00ff88)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🎉 寰宇多市场金融监控系统 - 测试页面
        </h1>
        
        <div style={{ marginTop: '30px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '15px', color: '#00ff88' }}>
            ✅ React 正常运行
          </h2>
          <p style={{ fontSize: '16px', color: '#8a94a6', marginBottom: '10px' }}>
            当前时间: {new Date().toLocaleString('zh-CN')}
          </p>
          <p style={{ fontSize: '16px', color: '#8a94a6' }}>
            如果您能看到这个页面，说明：
          </p>
          <ul style={{ fontSize: '16px', color: '#8a94a6', marginLeft: '20px', marginTop: '10px' }}>
            <li>✅ 前端服务器运行正常</li>
            <li>✅ React 渲染正常</li>
            <li>✅ 路由系统工作正常</li>
            <li>✅ CSS 样式加载正常</li>
          </ul>
        </div>

        <div style={{ marginTop: '30px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '15px', color: '#00ccff' }}>
            🔗 快速导航
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <a href="/" style={{ 
              color: '#00ff88', 
              textDecoration: 'none',
              fontSize: '18px',
              padding: '10px',
              background: 'rgba(0, 255, 136, 0.1)',
              borderRadius: '8px',
              display: 'block'
            }}>
              📊 返回首页 (K线仪表盘)
            </a>
            <a href="/financial-monitoring" style={{ 
              color: '#00ff88', 
              textDecoration: 'none',
              fontSize: '18px',
              padding: '10px',
              background: 'rgba(0, 255, 136, 0.1)',
              borderRadius: '8px',
              display: 'block'
            }}>
              💹 金融监控系统
            </a>
            <a href="/assistant" style={{ 
              color: '#00ccff', 
              textDecoration: 'none',
              fontSize: '18px',
              padding: '10px',
              background: 'rgba(0, 204, 255, 0.1)',
              borderRadius: '8px',
              display: 'block'
            }}>
              🤖 助手模式 (简化界面)
            </a>
          </div>
        </div>

        <div style={{ 
          marginTop: '40px', 
          padding: '20px', 
          background: 'rgba(255, 170, 0, 0.1)',
          border: '1px solid #ffaa00',
          borderRadius: '8px'
        }}>
          <h3 style={{ fontSize: '20px', color: '#ffaa00', marginBottom: '10px' }}>
            ⚠️ 如果其他页面看不到内容
          </h3>
          <p style={{ fontSize: '14px', color: '#8a94a6' }}>
            可能的原因：
          </p>
          <ol style={{ fontSize: '14px', color: '#8a94a6', marginLeft: '20px', marginTop: '10px' }}>
            <li>后端服务未启动 → 检查 http://localhost:8000/docs</li>
            <li>WebSocket 连接失败 → 查看浏览器控制台 (F12)</li>
            <li>数据加载中 → 等待几秒钟</li>
            <li>浏览器缓存问题 → 按 Ctrl+Shift+R 强制刷新</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default TestPage;
