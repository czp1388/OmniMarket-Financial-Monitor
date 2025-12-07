/**
 * 图表绘图管理器
 * 处理绘图逻辑、存储、快捷键等
 */
import { useEffect, useCallback, useRef } from 'react';
import { DrawingTool, Drawing } from '../components/DrawingToolbar';

// 斐波那契回调比例
const FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];

interface UseDrawingManagerProps {
  chartRef: React.RefObject<any>;
  onDrawingsChange?: (drawings: Drawing[]) => void;
}

export const useDrawingManager = ({
  chartRef,
  onDrawingsChange,
}: UseDrawingManagerProps) => {
  const drawingsRef = useRef<Drawing[]>([]);
  const activeToolRef = useRef<DrawingTool>(DrawingTool.NONE);
  const currentDrawingRef = useRef<Partial<Drawing> | null>(null);
  const isDrawingRef = useRef(false);

  // 生成唯一ID
  const generateId = () => `drawing-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // 添加绘图对象
  const addDrawing = useCallback((drawing: Drawing) => {
    drawingsRef.current = [...drawingsRef.current, drawing];
    onDrawingsChange?.(drawingsRef.current);
    localStorage.setItem('chartDrawings', JSON.stringify(drawingsRef.current));
  }, [onDrawingsChange]);

  // 删除绘图对象
  const removeDrawing = useCallback((id: string) => {
    drawingsRef.current = drawingsRef.current.filter(d => d.id !== id);
    onDrawingsChange?.(drawingsRef.current);
    localStorage.setItem('chartDrawings', JSON.stringify(drawingsRef.current));
  }, [onDrawingsChange]);

  // 清除所有绘图
  const clearAllDrawings = useCallback(() => {
    drawingsRef.current = [];
    onDrawingsChange?.([]);
    localStorage.removeItem('chartDrawings');
  }, [onDrawingsChange]);

  // 设置当前工具
  const setActiveTool = useCallback((tool: DrawingTool) => {
    activeToolRef.current = tool;
    if (tool === DrawingTool.NONE) {
      isDrawingRef.current = false;
      currentDrawingRef.current = null;
    }
  }, []);

  // 绘制趋势线
  const drawTrendLine = useCallback((start: { x: number; y: number }, end: { x: number; y: number }) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.TREND_LINE,
      points: [start, end],
      color: '#00ccff',
      thickness: 2,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 绘制水平线
  const drawHorizontalLine = useCallback((y: number) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.HORIZONTAL_LINE,
      points: [{ x: 0, y }],
      color: '#ff4444',
      thickness: 1,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 绘制垂直线
  const drawVerticalLine = useCallback((x: number) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.VERTICAL_LINE,
      points: [{ x, y: 0 }],
      color: '#00ff88',
      thickness: 1,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 绘制斐波那契回调
  const drawFibonacci = useCallback((start: { x: number; y: number }, end: { x: number; y: number }) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.FIBONACCI,
      points: [start, end],
      color: '#ffaa00',
      thickness: 1,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 添加文本标注
  const addTextAnnotation = useCallback((point: { x: number; y: number }, text: string) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.TEXT,
      points: [point],
      color: '#ffffff',
      text,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 绘制箭头
  const drawArrow = useCallback((start: { x: number; y: number }, end: { x: number; y: number }) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.ARROW,
      points: [start, end],
      color: '#00ff88',
      thickness: 2,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 绘制矩形
  const drawRectangle = useCallback((start: { x: number; y: number }, end: { x: number; y: number }) => {
    const drawing: Drawing = {
      id: generateId(),
      type: DrawingTool.RECTANGLE,
      points: [start, end],
      color: '#00ccff',
      thickness: 1,
    };
    addDrawing(drawing);
  }, [addDrawing]);

  // 渲染绘图到 ECharts
  const renderDrawingsToChart = useCallback(() => {
    if (!chartRef.current) return;

    const chart = chartRef.current;
    const markLines: any[] = [];
    const markPoints: any[] = [];

    drawingsRef.current.forEach(drawing => {
      switch (drawing.type) {
        case DrawingTool.TREND_LINE:
          if (drawing.points.length === 2) {
            markLines.push({
              type: 'line',
              x: drawing.points[0].x,
              y: drawing.points[0].y,
              x2: drawing.points[1].x,
              y2: drawing.points[1].y,
              lineStyle: {
                color: drawing.color,
                width: drawing.thickness,
              },
            });
          }
          break;

        case DrawingTool.HORIZONTAL_LINE:
          markLines.push({
            yAxis: drawing.points[0].y,
            lineStyle: {
              color: drawing.color,
              width: drawing.thickness,
              type: 'solid',
            },
          });
          break;

        case DrawingTool.VERTICAL_LINE:
          markLines.push({
            xAxis: drawing.points[0].x,
            lineStyle: {
              color: drawing.color,
              width: drawing.thickness,
              type: 'solid',
            },
          });
          break;

        case DrawingTool.FIBONACCI:
          if (drawing.points.length === 2) {
            const start = drawing.points[0];
            const end = drawing.points[1];
            const diff = end.y - start.y;

            FIBONACCI_LEVELS.forEach(level => {
              const y = start.y + diff * level;
              markLines.push({
                yAxis: y,
                label: {
                  formatter: `Fib ${(level * 100).toFixed(1)}%`,
                  position: 'end',
                },
                lineStyle: {
                  color: drawing.color,
                  width: 1,
                  type: level === 0 || level === 1 ? 'solid' : 'dashed',
                },
              });
            });
          }
          break;

        case DrawingTool.TEXT:
          markPoints.push({
            coord: [drawing.points[0].x, drawing.points[0].y],
            label: {
              show: true,
              formatter: drawing.text || '',
              color: drawing.color,
              backgroundColor: '#000',
              padding: 4,
              borderRadius: 3,
            },
          });
          break;

        // 其他类型的绘图可以在这里添加
      }
    });

    // 更新图表配置
    chart.setOption({
      series: [
        {
          markLine: {
            data: markLines,
            silent: false,
          },
          markPoint: {
            data: markPoints,
            silent: false,
          },
        },
      ],
    });
  }, [chartRef]);

  // 快捷键处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Esc - 取消当前工具
      if (e.key === 'Escape') {
        setActiveTool(DrawingTool.NONE);
      }
      
      // Ctrl+D - 清除所有绘图
      if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        clearAllDrawings();
      }

      // 快捷键切换工具
      if (!e.ctrlKey && !e.altKey) {
        switch (e.key.toLowerCase()) {
          case 't':
            setActiveTool(DrawingTool.TREND_LINE);
            break;
          case 'h':
            setActiveTool(DrawingTool.HORIZONTAL_LINE);
            break;
          case 'v':
            setActiveTool(DrawingTool.VERTICAL_LINE);
            break;
          case 'f':
            setActiveTool(DrawingTool.FIBONACCI);
            break;
          case 'x':
            setActiveTool(DrawingTool.TEXT);
            break;
          case 'a':
            setActiveTool(DrawingTool.ARROW);
            break;
          case 'r':
            setActiveTool(DrawingTool.RECTANGLE);
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setActiveTool, clearAllDrawings]);

  // 从 localStorage 加载绘图
  useEffect(() => {
    const saved = localStorage.getItem('chartDrawings');
    if (saved) {
      try {
        drawingsRef.current = JSON.parse(saved);
        onDrawingsChange?.(drawingsRef.current);
      } catch (e) {
        console.error('Failed to load drawings:', e);
      }
    }
  }, [onDrawingsChange]);

  return {
    drawings: drawingsRef.current,
    activeTool: activeToolRef.current,
    setActiveTool,
    addDrawing,
    removeDrawing,
    clearAllDrawings,
    drawTrendLine,
    drawHorizontalLine,
    drawVerticalLine,
    drawFibonacci,
    addTextAnnotation,
    drawArrow,
    drawRectangle,
    renderDrawingsToChart,
  };
};

export default useDrawingManager;
