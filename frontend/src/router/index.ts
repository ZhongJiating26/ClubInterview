import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import InterviewerLayout from '@/layouts/InterviewerLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useUserStore } from '@/stores/user'

// 公开页面，不需要登录
const publicPaths = ['/login', '/register', '/forget-password', '/role-select', '/init', '/404']

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    // 根路径由路由守卫处理重定向
  },
  // 登录页（无布局）
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  // 注册页（无布局）
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  // 忘记密码页（无布局）
  {
    path: '/forget-password',
    name: 'ForgetPassword',
    component: () => import('@/views/ForgetPassword.vue'),
    meta: { title: '忘记密码' }
  },
  // 角色选择页（无布局）
  {
    path: '/role-select',
    name: 'RoleSelect',
    component: () => import('@/views/RoleSelect.vue'),
    meta: { title: '选择角色' }
  },
  // 用户信息初始化页（无布局）
  {
    path: '/init',
    name: 'Init',
    component: () => import('@/views/Init.vue'),
    meta: { title: '初始化信息' }
  },
  // 管理员端（电脑web端布局）
  {
    path: '/admin',
    component: AdminLayout,
    meta: { roles: ['admin'] },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '仪表盘', roles: ['admin'] }
      },
      {
        path: 'applications',
        name: 'Applications',
        component: () => import('@/views/admin/Applications.vue'),
        meta: { title: '报名管理', roles: ['admin'] },
        redirect: { name: 'ApplicationsCreate' },
        children: [
          {
            path: 'create',
            name: 'ApplicationsCreate',
            component: () => import('@/views/admin/applications/Create.vue'),
            meta: { title: '发布报名', roles: ['admin'] }
          },
          {
            path: 'session/:id',
            name: 'SessionWizard',
            component: () => import('@/views/admin/applications/SessionWizard.vue'),
            meta: { title: '招新场次向导', roles: ['admin'] }
          },
          {
            path: 'history',
            name: 'ApplicationsHistory',
            component: () => import('@/views/admin/applications/History.vue'),
            meta: { title: '历史报名记录', roles: ['admin'] }
          },
          {
            path: 'review',
            name: 'ApplicationsReview',
            component: () => import('@/views/admin/applications/Review.vue'),
            meta: { title: '报名审核', roles: ['admin'] }
          }
        ]
      },
      {
        path: 'interviews',
        name: 'Interviews',
        component: () => import('@/views/admin/Interviews.vue'),
        meta: { title: '面试管理', roles: ['admin'] },
        redirect: { name: 'InterviewsList' },
        children: [
          {
            path: 'list',
            name: 'InterviewsList',
            component: () => import('@/views/admin/interviews/List.vue'),
            meta: { title: '面试场次', roles: ['admin'] }
          },
          {
            path: 'wizard',
            name: 'InterviewsWizard',
            component: () => import('@/views/admin/interviews/Wizard.vue'),
            meta: { title: '发布面试', roles: ['admin'] }
          },
          {
            path: 'records',
            name: 'InterviewsRecords',
            component: () => import('@/views/admin/interviews/Records.vue'),
            meta: { title: '面试记录', roles: ['admin'] }
          },
          {
            path: 'filter',
            name: 'InterviewsFilter',
            component: () => import('@/views/admin/interviews/Filter.vue'),
            meta: { title: '面试筛选', roles: ['admin'] }
          }
        ]
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/admin/Statistics.vue'),
        meta: { title: '数据统计', roles: ['admin'] }
      },
      {
        path: 'tickets',
        name: 'AdminTickets',
        component: () => import('@/views/admin/Tickets.vue'),
        meta: { title: '工单管理', roles: ['admin'] }
      },
      {
        path: 'clubs',
        name: 'Clubs',
        meta: { title: '社团管理', roles: ['admin'] },
        children: [
          {
            path: 'profile',
            name: 'ClubsProfile',
            component: () => import('@/views/admin/clubs/Profile.vue'),
            meta: { title: '社团资料', roles: ['admin'] }
          },
          {
            path: 'departments',
            name: 'ClubsDepartments',
            component: () => import('@/views/admin/clubs/Departments.vue'),
            meta: { title: '部门管理', roles: ['admin'] }
          },
          {
            path: 'positions',
            name: 'ClubsPositions',
            component: () => import('@/views/admin/clubs/Positions.vue'),
            meta: { title: '岗位管理', roles: ['admin'] }
          },
          {
            path: 'members',
            name: 'ClubsMembers',
            component: () => import('@/views/admin/clubs/Members.vue'),
            meta: { title: '社团人员管理', roles: ['admin'] }
          }
        ]
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/settings/Settings.vue'),
        meta: { title: '系统设置', roles: ['admin'] }
      }
    ]
  },
  // 面试官端（电脑web端布局）
  {
    path: '/interviewer',
    component: InterviewerLayout,
    meta: { roles: ['interviewer'] },
    redirect: { name: 'InterviewerJoin' },
    children: [
      {
        path: 'join',
        name: 'InterviewerJoin',
        component: () => import('@/views/interviewer/Join.vue'),
        meta: { title: '加入社团', roles: ['interviewer'] }
      },
      {
        path: 'applications',
        name: 'InterviewerApplications',
        component: () => import('@/views/interviewer/Applications.vue'),
        meta: { title: '报名管理', roles: ['interviewer'] },
        redirect: { name: 'InterviewerApplicationsSessions' },
        children: [
          {
            path: 'sessions',
            name: 'InterviewerApplicationsSessions',
            component: () => import('@/views/interviewer/applications/Sessions.vue'),
            meta: { title: '报名场次', roles: ['interviewer'] }
          },
          {
            path: 'session/:id',
            name: 'InterviewerApplicationSessionDetail',
            component: () => import('@/views/interviewer/applications/SessionDetail.vue'),
            meta: { title: '场次详情', roles: ['interviewer'] }
          },
          {
            path: 'history',
            name: 'InterviewerApplicationsHistory',
            component: () => import('@/views/interviewer/applications/History.vue'),
            meta: { title: '历史报名记录', roles: ['interviewer'] }
          }
        ]
      },
      {
        path: 'interviews',
        name: 'InterviewerInterviews',
        component: () => import('@/views/interviewer/Interviews.vue'),
        meta: { title: '面试管理', roles: ['interviewer'] },
        redirect: { name: 'InterviewerInterviewsList' },
        children: [
          {
            path: 'list',
            name: 'InterviewerInterviewsList',
            component: () => import('@/views/interviewer/interviews/List.vue'),
            meta: { title: '面试场次', roles: ['interviewer'] }
          },
          {
            path: 'score',
            name: 'InterviewerInterviewsScore',
            component: () => import('@/views/interviewer/interviews/Score.vue'),
            meta: { title: '面试评分', roles: ['interviewer'] }
          },
          {
            path: 'records',
            name: 'InterviewerInterviewsRecords',
            component: () => import('@/views/interviewer/interviews/Records.vue'),
            meta: { title: '面试记录', roles: ['interviewer'] }
          },
          {
            path: 'filter',
            name: 'InterviewerInterviewsFilter',
            component: () => import('@/views/interviewer/interviews/Filter.vue'),
            meta: { title: '面试筛选', roles: ['interviewer'] }
          }
        ]
      }
    ]
  },
  // 学生端（手机h5端布局）
  {
    path: '/student',
    component: StudentLayout,
    meta: { roles: ['student'] },
    children: [
      {
        path: 'home',
        name: 'StudentHome',
        component: () => import('@/views/student/Home.vue'),
        meta: { title: '首页', roles: ['student'] }
      },
      {
        path: 'club/:id',
        name: 'StudentClubDetail',
        component: () => import('@/views/student/ClubDetail.vue'),
        meta: { title: '社团详情', roles: ['student'] }
      },
      {
        path: 'apply/:id',
        name: 'StudentApply',
        component: () => import('@/views/student/Apply.vue'),
        meta: { title: '报名', roles: ['student'] }
      },
      {
        path: 'interviews',
        name: 'StudentInterviews',
        component: () => import('@/views/student/Interviews.vue'),
        meta: { title: '面试', roles: ['student'] }
      },
      {
        path: 'interviews/signup/:signupId',
        name: 'StudentSignupDetail',
        component: () => import('@/views/student/interviews/SignupDetail.vue'),
        meta: { title: '报名详情', roles: ['student'] }
      },
      {
        path: 'interviews/record/:candidateId',
        name: 'StudentInterviewRecordDetail',
        component: () => import('@/views/student/interviews/RecordDetail.vue'),
        meta: { title: '面试详情', roles: ['student'] }
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('@/views/student/Profile.vue'),
        meta: { title: '我的', roles: ['student'] }
      }
    ]
  },
  // 404 页面
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  },
  // 捕获所有未匹配路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：权限验证
router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title as string || '社团面试系统'} - 社团面试系统`

  const userStore = useUserStore()
  const isLoggedIn = !!userStore.token

  // 公开页面直接放行
  if (publicPaths.includes(to.path)) {
    // 如果已登录访问登录页，跳转到首页
    if (isLoggedIn && to.path === '/login') {
      // 确保有用户信息
      if (!userStore.userInfo) {
        try {
          const { getMe } = await import('@/api/modules/auth')
          const userData = await getMe()
          userStore.setUserInfo(userData)
        } catch {
          next('/login')
          return
        }
      }
      const role = userStore.primaryRole || 'student'
      const homeMap: Record<string, string> = {
        admin: '/admin/dashboard',
        interviewer: '/interviewer/join',
        student: '/student/home'
      }
      next(homeMap[role] || '/student/home')
    } else {
      next()
    }
    return
  }

  // 未登录则跳转到登录页
  if (!isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 确保有用户信息
  if (!userStore.userInfo) {
    try {
      const { getMe } = await import('@/api/modules/auth')
      const userData = await getMe()
      userStore.setUserInfo(userData)
    } catch {
      userStore.logout()
      next('/login')
      return
    }
  }

  // 根路径跳转到首页
  if (to.path === '/') {
    const userRoles = userStore.userInfo?.roles?.map(r => r.code.toLowerCase()) || []

    // 根据用户实际角色跳转
    if (userRoles.includes('club_admin') || userRoles.includes('admin')) {
      next('/admin/dashboard')
    } else if (userRoles.includes('interviewer')) {
      next('/interviewer/join')
    } else {
      next('/student/home')
    }
    return
  }

  // 检查角色权限
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && requiredRoles.length > 0) {
    const userRoles = userStore.userInfo?.roles?.map(r => r.code.toUpperCase()) || []

    // 检查是否有权限（需要匹配后端的角色代码）
    const hasPermission = requiredRoles.some(requiredRole => {
      const upperRequired = requiredRole.toUpperCase()
      // 支持多种角色代码格式
      return userRoles.some(userRole => {
        // 后端返回 CLUB_ADMIN, INTERVIEWER, STUDENT
        if (upperRequired === 'ADMIN') {
          return userRole === 'CLUB_ADMIN' || userRole === 'ADMIN'
        }
        return userRole === upperRequired
      })
    })

    if (!hasPermission) {
      // 无权限，跳转到第一个有权限的页面（只跳转一次，避免循环）
      // 如果目标就是首页，说明用户没有任何有效角色，跳转到登录页
      if (to.path === '/student/home' || to.path === '/admin/dashboard' || to.path === '/interviewer/join') {
        userStore.logout()
        next('/login')
        return
      }

      const userRolesLower = userStore.userInfo?.roles?.map(r => r.code.toLowerCase()) || []
      if (userRolesLower.includes('club_admin') || userRolesLower.includes('admin')) {
        next('/admin/dashboard')
      } else if (userRolesLower.includes('interviewer')) {
        next('/interviewer/join')
      } else {
        next('/student/home')
      }
      return
    }
  }

  next()
})

export default router
