/**
 * 图表绘图工具栏组件
 * 实现趋势线、斐波那契、文本标注等绘图功能
 */
import React, { useState } from 'react';

// 绘图工具类型
export enum DrawingTool {
  NONE = 'none',
  TREND_LINE = 'trendLine',
  HORIZONTAL_LINE = 'horizontalLine',
  VERTICAL_LINE = 'verticalLine',
  FIBONACCI = 'fibonacci',
  TEXT = 'text',
  ARROW = 'arrow',
  RECTANGLE = 'rectangle',
}

// 绘图对象接口
export interface Drawing {
  id: string;
  type: DrawingTool;
  points: Array<{ x: number; y: number }>;
  color: string;
  text?: string;
  thickness?: number;
}

interface DrawingToolbarProps {
  onToolSelect: (tool: DrawingTool) => void;
  onClearAll: () => void;
  activeTool: DrawingTool;
}

const DrawingToolbar: React.FC<DrawingToolbarProps> = ({
  onToolSelect,
  onClearAll,
  activeTool,
}) => {
  const [showTooltip, setShowTooltip] = useState<string | null>(null);

  const tools = [
    { type: DrawingTool.TREND_LINE, icon: '📈', label: '趋势线', hotkey: 'T' },
    { type: DrawingTool.HORIZONTAL_LINE, icon: '━', label: '水平线', hotkey: 'H' },
    { type: DrawingTool.VERTICAL_LINE, icon: '┃', label: '垂直线', hotkey: 'V' },
    { type: DrawingTool.FIBONACCI, icon: '🌀', label: '斐波那契', hotkey: 'F' },
    { type: DrawingTool.TEXT, icon: '📝', label: '文本标注', hotkey: 'X' },
    { type: DrawingTool.ARROW, icon: '➜', label: '箭头', hotkey: 'A' },
    { type: DrawingTool.RECTANGLE, icon: '▭', label: '矩形', hotkey: 'R' },
  ];

  return (
    <div className="drawing-toolbar" style={styles.toolbar}>
      {/* 工具选择按钮 */}
      <div style={styles.toolGroup}>
        {tools.map((tool) => (
          <button
            key={tool.type}
            className={`tool-btn ${activeTool === tool.type ? 'active' : ''}`}
            onClick={() => onToolSelect(tool.type)}
            onMouseEnter={() => setShowTooltip(tool.type)}
            onMouseLeave={() => setShowTooltip(null)}
            style={{
              ...styles.toolButton,
              ...(activeTool === tool.type ? styles.activeButton : {}),
            }}
            title={`${tool.label} (${tool.hotkey})`}
          >
            <span style={styles.icon}>{tool.icon}</span>
            {showTooltip === tool.type && (
              <div style={styles.tooltip}>
                {tool.label} ({tool.hotkey})
              </div>
            )}
          </button>
        ))}
      </div>

      {/* 分隔线 */}
      <div style={styles.separator} />

      {/* 操作按钮 */}
      <div style={styles.actionGroup}>
        <button
          className="tool-btn"
          onClick={() => onToolSelect(DrawingTool.NONE)}
          style={{
            ...styles.toolButton,
            ...(activeTool === DrawingTool.NONE ? styles.activeButton : {}),
          }}
          title="选择工具 (Esc)"
        >
          <span style={styles.icon}>🖱️</span>
        </button>
        
        <button
          className="tool-btn clear-btn"
          onClick={onClearAll}
          style={styles.clearButton}
          title="清除所有绘图 (Ctrl+D)"
        >
          <span style={styles.icon}>🗑️</span>
        </button>
      </div>
    </div>
  );
};

// 样式定义
const styles: { [key: string]: React.CSSProperties } = {
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    background: '#141a2a',
    border: '1px solid #2a3a5a',
    borderRadius: '4px',
    fontFamily: "'Courier New', monospace",
  },
  toolGroup: {
    display: 'flex',
    gap: '4px',
  },
  toolButton: {
    padding: '6px 10px',
    background: 'transparent',
    border: '1px solid #2a3a5a',
    borderRadius: '3px',
    color: '#fff',
    cursor: 'pointer',
    transition: 'all 0.2s',
    position: 'relative' as const,
  },
  activeButton: {
    background: '#00ccff',
    borderColor: '#00ccff',
  },
  icon: {
    fontSize: '16px',
  },
  tooltip: {
    position: 'absolute' as const,
    top: '-30px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: '#000',
    color: '#fff',
    padding: '4px 8px',
    borderRadius: '3px',
    fontSize: '11px',
    whiteSpace: 'nowrap' as const,
    zIndex: 1000,
  },
  separator: {
    width: '1px',
    height: '24px',
    background: '#2a3a5a',
  },
  actionGroup: {
    display: 'flex',
    gap: '4px',
    marginLeft: 'auto',
  },
  clearButton: {
    padding: '6px 10px',
    background: 'transparent',
    border: '1px solid #ff4444',
    borderRadius: '3px',
    color: '#ff4444',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
};

export default DrawingToolbar;
