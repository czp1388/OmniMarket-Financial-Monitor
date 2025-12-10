// Zustand状态管理优化
import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

/**
 * 市场数据状态
 */
interface MarketDataState {
  // 数据
  tickers: Record<string, any>;
  klines: Record<string, any[]>;
  
  // 订阅管理
  subscriptions: Set<string>;
  
  // 加载状态
  loading: Record<string, boolean>;
  errors: Record<string, string | null>;
  
  // Actions
  setTicker: (symbol: string, data: any) => void;
  setKlines: (symbol: string, data: any[]) => void;
  subscribe: (symbol: string) => void;
  unsubscribe: (symbol: string) => void;
  setLoading: (key: string, loading: boolean) => void;
  setError: (key: string, error: string | null) => void;
  clear: () => void;
}

/**
 * 优化的市场数据Store
 * - 使用immer简化不可变更新
 * - 使用subscribeWithSelector优化订阅
 * - 持久化部分状态
 */
export const useMarketDataStore = create<MarketDataState>()(
  devtools(
    subscribeWithSelector(
      immer((set) => ({
        tickers: {},
        klines: {},
        subscriptions: new Set(),
        loading: {},
        errors: {},
        
        setTicker: (symbol, data) =>
          set((state) => {
            state.tickers[symbol] = data;
          }),
        
        setKlines: (symbol, data) =>
          set((state) => {
            state.klines[symbol] = data;
          }),
        
        subscribe: (symbol) =>
          set((state) => {
            state.subscriptions.add(symbol);
          }),
        
        unsubscribe: (symbol) =>
          set((state) => {
            state.subscriptions.delete(symbol);
          }),
        
        setLoading: (key, loading) =>
          set((state) => {
            state.loading[key] = loading;
          }),
        
        setError: (key, error) =>
          set((state) => {
            state.errors[key] = error;
          }),
        
        clear: () =>
          set((state) => {
            state.tickers = {};
            state.klines = {};
            state.subscriptions.clear();
            state.loading = {};
            state.errors = {};
          }),
      }))
    ),
    { name: 'MarketDataStore' }
  )
);

/**
 * 预警状态
 */
interface AlertState {
  alerts: any[];
  statistics: any | null;
  triggers: any[];
  
  // Actions
  setAlerts: (alerts: any[]) => void;
  addAlert: (alert: any) => void;
  updateAlert: (id: number, updates: any) => void;
  removeAlert: (id: number) => void;
  setStatistics: (stats: any) => void;
  setTriggers: (triggers: any[]) => void;
}

export const useAlertStore = create<AlertState>()(
  devtools(
    persist(
      immer((set) => ({
        alerts: [],
        statistics: null,
        triggers: [],
        
        setAlerts: (alerts) =>
          set((state) => {
            state.alerts = alerts;
          }),
        
        addAlert: (alert) =>
          set((state) => {
            state.alerts.push(alert);
          }),
        
        updateAlert: (id, updates) =>
          set((state) => {
            const index = state.alerts.findIndex((a) => a.id === id);
            if (index !== -1) {
              state.alerts[index] = { ...state.alerts[index], ...updates };
            }
          }),
        
        removeAlert: (id) =>
          set((state) => {
            state.alerts = state.alerts.filter((a) => a.id !== id);
          }),
        
        setStatistics: (stats) =>
          set((state) => {
            state.statistics = stats;
          }),
        
        setTriggers: (triggers) =>
          set((state) => {
            state.triggers = triggers;
          }),
      })),
      {
        name: 'alert-storage',
        partialize: (state) => ({ alerts: state.alerts }), // 仅持久化alerts
      }
    ),
    { name: 'AlertStore' }
  )
);

/**
 * UI状态（主题、布局等）
 */
interface UIState {
  theme: 'light' | 'dark' | 'bloomberg';
  sidebarCollapsed: boolean;
  activeTab: string;
  
  // Actions
  setTheme: (theme: 'light' | 'dark' | 'bloomberg') => void;
  toggleSidebar: () => void;
  setActiveTab: (tab: string) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'bloomberg',
      sidebarCollapsed: false,
      activeTab: 'dashboard',
      
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    {
      name: 'ui-storage',
    }
  )
);

/**
 * 性能优化的Selector Hook
 * 使用浅比较避免不必要的重渲染
 */
export function useShallowMarketData<T>(
  selector: (state: MarketDataState) => T
): T {
  return useMarketDataStore(selector, (a, b) => {
    if (typeof a === 'object' && typeof b === 'object') {
      return JSON.stringify(a) === JSON.stringify(b);
    }
    return a === b;
  });
}

/**
 * WebSocket状态管理
 */
interface WebSocketState {
  connected: boolean;
  subscriptions: Map<string, Set<(data: any) => void>>;
  lastMessage: any | null;
  
  // Actions
  setConnected: (connected: boolean) => void;
  subscribe: (symbol: string, callback: (data: any) => void) => void;
  unsubscribe: (symbol: string, callback: (data: any) => void) => void;
  handleMessage: (message: any) => void;
}

export const useWebSocketStore = create<WebSocketState>()(
  devtools(
    (set, get) => ({
      connected: false,
      subscriptions: new Map(),
      lastMessage: null,
      
      setConnected: (connected) => set({ connected }),
      
      subscribe: (symbol, callback) =>
        set((state) => {
          const subs = new Map(state.subscriptions);
          if (!subs.has(symbol)) {
            subs.set(symbol, new Set());
          }
          subs.get(symbol)!.add(callback);
          return { subscriptions: subs };
        }),
      
      unsubscribe: (symbol, callback) =>
        set((state) => {
          const subs = new Map(state.subscriptions);
          if (subs.has(symbol)) {
            subs.get(symbol)!.delete(callback);
            if (subs.get(symbol)!.size === 0) {
              subs.delete(symbol);
            }
          }
          return { subscriptions: subs };
        }),
      
      handleMessage: (message) => {
        set({ lastMessage: message });
        
        const { subscriptions } = get();
        const symbol = message.symbol || message.s;
        
        if (symbol && subscriptions.has(symbol)) {
          subscriptions.get(symbol)!.forEach((callback) => {
            callback(message);
          });
        }
      },
    }),
    { name: 'WebSocketStore' }
  )
);

/**
 * 性能监控Store
 */
interface PerformanceState {
  metrics: {
    renderCount: number;
    lastRenderTime: number;
    averageRenderTime: number;
  };
  
  recordRender: (duration: number) => void;
  reset: () => void;
}

export const usePerformanceStore = create<PerformanceState>()((set) => ({
  metrics: {
    renderCount: 0,
    lastRenderTime: 0,
    averageRenderTime: 0,
  },
  
  recordRender: (duration) =>
    set((state) => {
      const newCount = state.metrics.renderCount + 1;
      const newAverage =
        (state.metrics.averageRenderTime * state.metrics.renderCount + duration) / newCount;
      
      return {
        metrics: {
          renderCount: newCount,
          lastRenderTime: duration,
          averageRenderTime: newAverage,
        },
      };
    }),
  
  reset: () =>
    set({
      metrics: {
        renderCount: 0,
        lastRenderTime: 0,
        averageRenderTime: 0,
      },
    }),
}));
