// 虚拟滚动Hook - 用于长列表性能优化
import { useState, useEffect, useRef, useMemo } from 'react';

export interface VirtualScrollConfig {
  itemHeight: number;          // 单项高度（像素）
  containerHeight: number;     // 容器高度（像素）
  overscan?: number;           // 预渲染项数（上下各多渲染几项）
  totalItems: number;          // 总项数
}

export interface VirtualScrollResult {
  virtualItems: Array<{
    index: number;
    offsetTop: number;
  }>;
  totalHeight: number;
  scrollTop: number;
  containerRef: React.RefObject<HTMLDivElement>;
}

/**
 * 虚拟滚动Hook
 * 
 * @example
 * const { virtualItems, totalHeight, containerRef } = useVirtualScroll({
 *   itemHeight: 50,
 *   containerHeight: 600,
 *   totalItems: 10000,
 *   overscan: 5
 * });
 */
export function useVirtualScroll(config: VirtualScrollConfig): VirtualScrollResult {
  const { itemHeight, containerHeight, overscan = 3, totalItems } = config;
  
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // 监听滚动事件
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };
    
    container.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, []);
  
  // 计算可见项
  const virtualItems = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      totalItems - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    const items = [];
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        offsetTop: i * itemHeight,
      });
    }
    
    return items;
  }, [scrollTop, itemHeight, containerHeight, overscan, totalItems]);
  
  const totalHeight = totalItems * itemHeight;
  
  return {
    virtualItems,
    totalHeight,
    scrollTop,
    containerRef,
  };
}

/**
 * 虚拟滚动组件（基于Hook的封装）
 * 
 * @example
 * <VirtualList
 *   items={dataArray}
 *   itemHeight={50}
 *   containerHeight={600}
 *   renderItem={(item, index) => <div>{item.name}</div>}
 * />
 */
interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
}

export function VirtualList<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 3,
  renderItem,
  className = '',
}: VirtualListProps<T>) {
  const { virtualItems, totalHeight, containerRef } = useVirtualScroll({
    itemHeight,
    containerHeight,
    totalItems: items.length,
    overscan,
  });
  
  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {virtualItems.map(({ index, offsetTop }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top: offsetTop,
              left: 0,
              right: 0,
              height: itemHeight,
            }}
          >
            {renderItem(items[index], index)}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * 动态高度虚拟滚动Hook（高级版）
 * 适用于不定高度的列表项
 */
interface DynamicVirtualScrollConfig {
  containerHeight: number;
  estimatedItemHeight: number;
  totalItems: number;
  overscan?: number;
  measureElement?: (index: number) => number;
}

export function useDynamicVirtualScroll(config: DynamicVirtualScrollConfig) {
  const {
    containerHeight,
    estimatedItemHeight,
    totalItems,
    overscan = 3,
    measureElement,
  } = config;
  
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const measurementsRef = useRef<Map<number, number>>(new Map());
  
  // 获取或估算项高度
  const getItemHeight = (index: number): number => {
    if (measurementsRef.current.has(index)) {
      return measurementsRef.current.get(index)!;
    }
    if (measureElement) {
      const height = measureElement(index);
      measurementsRef.current.set(index, height);
      return height;
    }
    return estimatedItemHeight;
  };
  
  // 计算项的偏移量
  const getItemOffset = (index: number): number => {
    let offset = 0;
    for (let i = 0; i < index; i++) {
      offset += getItemHeight(i);
    }
    return offset;
  };
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    
    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };
    
    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);
  
  const virtualItems = useMemo(() => {
    const items = [];
    let currentOffset = 0;
    let startIndex = 0;
    
    // 找到起始索引
    for (let i = 0; i < totalItems; i++) {
      const itemHeight = getItemHeight(i);
      if (currentOffset + itemHeight > scrollTop - overscan * estimatedItemHeight) {
        startIndex = i;
        break;
      }
      currentOffset += itemHeight;
    }
    
    // 收集可见项
    const endScrollTop = scrollTop + containerHeight + overscan * estimatedItemHeight;
    for (let i = startIndex; i < totalItems && currentOffset < endScrollTop; i++) {
      items.push({
        index: i,
        offsetTop: currentOffset,
        height: getItemHeight(i),
      });
      currentOffset += getItemHeight(i);
    }
    
    return items;
  }, [scrollTop, containerHeight, totalItems, overscan, estimatedItemHeight]);
  
  const totalHeight = useMemo(() => {
    let height = 0;
    for (let i = 0; i < totalItems; i++) {
      height += getItemHeight(i);
    }
    return height;
  }, [totalItems]);
  
  return {
    virtualItems,
    totalHeight,
    scrollTop,
    containerRef,
    measureItem: (index: number, height: number) => {
      measurementsRef.current.set(index, height);
    },
  };
}
