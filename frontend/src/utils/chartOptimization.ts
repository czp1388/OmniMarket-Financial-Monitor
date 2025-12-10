// ECharts 懒加载和性能优化工具
import { useEffect, useRef, useState, useCallback } from 'react';
import * as echarts from 'echarts/core';
import type { EChartsOption, ECharts } from 'echarts';

/**
 * ECharts懒加载Hook
 * 仅在组件可见时才初始化图表，减少首屏加载时间
 */
export function useLazyChart() {
  const chartRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<ECharts | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [isReady, setIsReady] = useState(false);
  
  // 使用IntersectionObserver检测可见性
  useEffect(() => {
    const element = chartRef.current;
    if (!element) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !isVisible) {
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.1 } // 10%可见时触发
    );
    
    observer.observe(element);
    
    return () => {
      observer.disconnect();
    };
  }, [isVisible]);
  
  // 初始化图表（仅在可见时）
  useEffect(() => {
    if (!isVisible || !chartRef.current) return;
    
    instanceRef.current = echarts.init(chartRef.current);
    setIsReady(true);
    
    return () => {
      instanceRef.current?.dispose();
      instanceRef.current = null;
    };
  }, [isVisible]);
  
  const setOption = useCallback((option: EChartsOption, opts?: any) => {
    if (instanceRef.current && isReady) {
      instanceRef.current.setOption(option, opts);
    }
  }, [isReady]);
  
  return {
    chartRef,
    instance: instanceRef.current,
    isReady,
    setOption,
  };
}

/**
 * 图表性能优化配置
 */
export const CHART_PERFORMANCE_CONFIG = {
  // 数据采样（大数据量时使用）
  sampling: {
    lttb: 'lttb',      // 最大三角形三桶采样算法
    average: 'average', // 平均值采样
    max: 'max',        // 最大值采样
    min: 'min',        // 最小值采样
  },
  
  // 大数据量优化选项
  largeDataOptimization: {
    large: true,              // 启用大数据量优化
    largeThreshold: 2000,     // 大数据量阈值
    progressive: 1000,        // 渐进式渲染
    progressiveThreshold: 3000, // 渐进式阈值
    progressiveChunkMode: 'mod' as const,
  },
  
  // 动画配置（性能优先）
  performanceAnimation: {
    animation: false,          // 关闭动画
    animationDuration: 0,
    animationEasing: 'linear' as const,
  },
  
  // 懒更新配置
  lazyUpdate: {
    lazyUpdate: true,
  },
};

/**
 * 创建性能优化的图表配置
 */
export function createOptimizedChartOption(
  baseOption: EChartsOption,
  dataSize: number = 0
): EChartsOption {
  const isLargeData = dataSize > CHART_PERFORMANCE_CONFIG.largeDataOptimization.largeThreshold;
  
  return {
    ...baseOption,
    // 大数据量时应用优化
    ...(isLargeData ? {
      animation: false,
      series: Array.isArray(baseOption.series)
        ? baseOption.series.map((s: any) => ({
            ...s,
            large: true,
            largeThreshold: CHART_PERFORMANCE_CONFIG.largeDataOptimization.largeThreshold,
            progressive: CHART_PERFORMANCE_CONFIG.largeDataOptimization.progressive,
            progressiveThreshold: CHART_PERFORMANCE_CONFIG.largeDataOptimization.progressiveThreshold,
            sampling: 'lttb', // 使用LTTB采样
          }))
        : baseOption.series,
    } : {}),
  };
}

/**
 * 图表数据采样工具
 * 用于减少渲染的数据点数量
 */
export function sampleChartData<T extends { timestamp?: number; time?: number }>(
  data: T[],
  maxPoints: number = 500
): T[] {
  if (data.length <= maxPoints) return data;
  
  const step = Math.ceil(data.length / maxPoints);
  return data.filter((_, index) => index % step === 0);
}

/**
 * LTTB (Largest Triangle Three Buckets) 采样算法
 * 保留数据的视觉特征
 */
export function lttbSample<T extends Record<string, any>>(
  data: T[],
  threshold: number,
  xKey: string = 'timestamp',
  yKey: string = 'value'
): T[] {
  if (data.length <= threshold || threshold <= 2) {
    return data;
  }
  
  const sampled: T[] = [];
  const bucketSize = (data.length - 2) / (threshold - 2);
  
  sampled.push(data[0]); // 始终保留第一个点
  
  let a = 0;
  
  for (let i = 0; i < threshold - 2; i++) {
    const avgRangeStart = Math.floor((i + 1) * bucketSize) + 1;
    const avgRangeEnd = Math.min(Math.floor((i + 2) * bucketSize) + 1, data.length);
    
    let avgX = 0;
    let avgY = 0;
    let avgRangeLength = 0;
    
    for (let j = avgRangeStart; j < avgRangeEnd; j++) {
      avgX += data[j][xKey];
      avgY += data[j][yKey];
      avgRangeLength++;
    }
    
    avgX /= avgRangeLength;
    avgY /= avgRangeLength;
    
    const rangeOffs = Math.floor((i + 0) * bucketSize) + 1;
    const rangeTo = Math.floor((i + 1) * bucketSize) + 1;
    
    const pointAX = data[a][xKey];
    const pointAY = data[a][yKey];
    
    let maxArea = -1;
    let maxAreaPoint = 0;
    
    for (let j = rangeOffs; j < rangeTo; j++) {
      const area = Math.abs(
        (pointAX - avgX) * (data[j][yKey] - pointAY) -
        (pointAX - data[j][xKey]) * (avgY - pointAY)
      ) * 0.5;
      
      if (area > maxArea) {
        maxArea = area;
        maxAreaPoint = j;
      }
    }
    
    sampled.push(data[maxAreaPoint]);
    a = maxAreaPoint;
  }
  
  sampled.push(data[data.length - 1]); // 始终保留最后一个点
  
  return sampled;
}

/**
 * 防抖更新Hook
 * 防止图表频繁重渲染
 */
export function useDebouncedChartUpdate(delay: number = 300) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const debouncedUpdate = useCallback(
    (updateFn: () => void) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        updateFn();
      }, delay);
    },
    [delay]
  );
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return debouncedUpdate;
}

/**
 * 图表响应式尺寸Hook
 */
export function useChartResize(chartInstance: ECharts | null) {
  useEffect(() => {
    if (!chartInstance) return;
    
    const handleResize = () => {
      chartInstance.resize();
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [chartInstance]);
}

/**
 * 图表主题懒加载
 */
export async function loadChartTheme(themeName: string) {
  try {
    const theme = await import(`echarts/theme/${themeName}.js`);
    echarts.registerTheme(themeName, theme.default);
    return true;
  } catch (error) {
    console.warn(`Failed to load chart theme: ${themeName}`, error);
    return false;
  }
}
