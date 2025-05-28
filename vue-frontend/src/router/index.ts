import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 懶加載組件
const Dashboard = () => import('@/views/Dashboard.vue')
const ChatInterface = () => import('@/views/ChatInterface.vue')
const AgentMonitor = () => import('@/views/AgentMonitor.vue')
const DataVisualization = () => import('@/views/DataVisualization.vue')
const FileManager = () => import('@/views/FileManager.vue')
const Settings = () => import('@/views/SettingsSimple.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '儀表板',
      requiresAuth: false
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatInterface,
    meta: {
      title: '聊天界面',
      requiresAuth: false
    }
  },
  {
    path: '/agents',
    name: 'AgentMonitor',
    component: AgentMonitor,
    meta: {
      title: '代理監控',
      requiresAuth: false
    }
  },
  {
    path: '/visualization',
    name: 'DataVisualization',
    component: DataVisualization,
    meta: {
      title: '數據視覺化',
      requiresAuth: false
    }
  },
  {
    path: '/files',
    name: 'FileManager',
    component: FileManager,
    meta: {
      title: '文件管理',
      requiresAuth: false
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: '設置',
      requiresAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '頁面未找到'
    }
  }
]

// 創建路由實例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守衛
router.beforeEach((to, from, next) => {
  // 設置頁面標題
  const title = to.meta?.title as string
  if (title) {
    document.title = `${title} - 多代理數據分析系統`
  }

  // 這裡可以添加認證檢查
  // if (to.meta.requiresAuth && !isAuthenticated()) {
  //   next('/login')
  //   return
  // }

  next()
})

// 路由錯誤處理
router.onError((error) => {
  console.error('路由錯誤:', error)
})

export default router