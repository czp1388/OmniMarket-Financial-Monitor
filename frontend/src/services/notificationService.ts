// 浏览器通知服务
class NotificationService {
  private static instance: NotificationService;
  private permission: NotificationPermission = 'default';
  private priceAlerts: Map<string, { target: number; direction: 'above' | 'below' }> = new Map();

  private constructor() {
    this.requestPermission();
  }

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  // 请求通知权限
  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('浏览器不支持通知功能');
      return false;
    }

    if (Notification.permission === 'granted') {
      this.permission = 'granted';
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      this.permission = permission;
      return permission === 'granted';
    }

    return false;
  }

  // 发送通知
  sendNotification(title: string, options?: NotificationOptions) {
    if (this.permission !== 'granted') {
      console.warn('通知权限未授予');
      return;
    }

    const notification = new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options,
    });

    // 点击通知时聚焦窗口
    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    // 3秒后自动关闭
    setTimeout(() => notification.close(), 3000);
  }

  // 设置价格预警
  setPriceAlert(symbol: string, targetPrice: number, direction: 'above' | 'below') {
    this.priceAlerts.set(symbol, { target: targetPrice, direction });
  }

  // 检查价格预警
  checkPriceAlert(symbol: string, currentPrice: number) {
    const alert = this.priceAlerts.get(symbol);
    if (!alert) return;

    const { target, direction } = alert;
    let triggered = false;

    if (direction === 'above' && currentPrice >= target) {
      triggered = true;
    } else if (direction === 'below' && currentPrice <= target) {
      triggered = true;
    }

    if (triggered) {
      this.sendNotification(`💰 ${symbol} 价格预警`, {
        body: `当前价格: $${currentPrice.toFixed(2)}\n目标价格: $${target.toFixed(2)}`,
        tag: symbol,
      });
      this.priceAlerts.delete(symbol);
    }
  }

  // 移除价格预警
  removePriceAlert(symbol: string) {
    this.priceAlerts.delete(symbol);
  }

  // 获取所有预警
  getAllAlerts() {
    return Array.from(this.priceAlerts.entries()).map(([symbol, alert]) => ({
      symbol,
      ...alert,
    }));
  }
}

export const notificationService = NotificationService.getInstance();
export default notificationService;
