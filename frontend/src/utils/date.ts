/**
 * 日期時間工具函數
 * 簡化版本，不依賴外部庫
 */

/**
 * 格式化日期時間為可讀格式
 * @param dateInput 日期字符串或 Date 對象
 * @param options 格式化選項
 * @returns 格式化後的日期字符串
 */
export const formatDateTime = (
  dateInput: string | Date,
  options?: Intl.DateTimeFormatOptions
): string => {
  try {
    let date: Date;
    
    if (typeof dateInput === 'string') {
      date = new Date(dateInput);
    } else {
      date = dateInput;
    }
    
    if (isNaN(date.getTime())) {
      return '無效日期';
    }
    
    const defaultOptions: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    };
    
    return date.toLocaleString('zh-TW', { ...defaultOptions, ...options });
  } catch (error) {
    console.error('日期格式化錯誤:', error);
    return '日期錯誤';
  }
};

/**
 * 格式化為相對時間（如：3分鐘前）
 * @param dateInput 日期字符串或 Date 對象
 * @returns 相對時間字符串
 */
export const formatRelativeTime = (dateInput: string | Date): string => {
  try {
    let date: Date;
    
    if (typeof dateInput === 'string') {
      date = new Date(dateInput);
    } else {
      date = dateInput;
    }
    
    if (isNaN(date.getTime())) {
      return '無效日期';
    }
    
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
      return `${days} 天前`;
    } else if (hours > 0) {
      return `${hours} 小時前`;
    } else if (minutes > 0) {
      return `${minutes} 分鐘前`;
    } else {
      return '剛剛';
    }
  } catch (error) {
    console.error('相對時間格式化錯誤:', error);
    return '時間錯誤';
  }
};

/**
 * 格式化日期（不包含時間）
 * @param dateInput 日期字符串或 Date 對象
 * @returns 格式化後的日期字符串
 */
export const formatDate = (dateInput: string | Date): string => {
  return formatDateTime(dateInput, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

/**
 * 格式化時間（不包含日期）
 * @param dateInput 日期字符串或 Date 對象
 * @returns 格式化後的時間字符串
 */
export const formatTime = (dateInput: string | Date): string => {
  return formatDateTime(dateInput, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
};

/**
 * 獲取當前時間的 ISO 字符串
 * @returns ISO 格式的當前時間字符串
 */
export const getCurrentISOString = (): string => {
  return new Date().toISOString();
};

/**
 * 檢查日期是否有效
 * @param dateInput 日期字符串或 Date 對象
 * @returns 是否為有效日期
 */
export const isValidDate = (dateInput: string | Date): boolean => {
  try {
    let date: Date;
    
    if (typeof dateInput === 'string') {
      date = new Date(dateInput);
    } else {
      date = dateInput;
    }
    
    return !isNaN(date.getTime());
  } catch {
    return false;
  }
};