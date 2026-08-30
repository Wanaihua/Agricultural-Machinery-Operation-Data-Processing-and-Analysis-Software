import { getCurrentUser, isAdminUser } from '@/utils/auth'

const adminOnlyPaths = ['/user', '/role', '/menu', '/file']

export function flattenMenus(menus = []) {
  const result = []

  const walk = (items) => {
    items.forEach((item) => {
      result.push(item)
      if (Array.isArray(item.children) && item.children.length) {
        walk(item.children)
      }
    })
  }

  walk(menus)
  return result
}

function normalizeRouteKey(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

export function hasRoutePermission(path) {
  const normalizedPath = String(path || '')
  // Always allow personal pages (修改密码 / 个人信息)
  if (normalizedPath === '/update-password' || normalizedPath === '/person-info' || normalizedPath === '/personInfo' || normalizedPath === '/personinfo') {
    return true
  }
  // Always allow data import and track pages to prevent accidental lockout
  if (normalizedPath === '/data/import' || normalizedPath.startsWith('/track')) {
    return true
  }
  // Allow viewing import logs page as well
  if (normalizedPath === '/import-log') {
    return true
  }
  if (adminOnlyPaths.includes(normalizedPath) && !isAdminUser(getCurrentUser())) {
    return false
  }

  const menus = JSON.parse(localStorage.getItem('menus') || '[]')
  if (!menus.length) {
    return (
      normalizedPath === '/home' ||
      normalizedPath === '/' ||
      normalizedPath === '/data/import' ||
      normalizedPath === '/import-log' ||
      normalizedPath.startsWith('/track')
    )
  }

  const flatMenus = flattenMenus(menus)
  const targetKey = normalizeRouteKey(normalizedPath)
  // Exact match or pagePath match
  if (flatMenus.some((item) => normalizeRouteKey(item.path) === targetKey || normalizeRouteKey(item.pagePath) === targetKey)) return true

  // Allow navigation to child routes under a menu path, e.g. /track/map/1 under /track
  const segments = normalizedPath.split('/')
  const base = segments.length > 1 ? `/${segments[1]}` : normalizedPath
  if (flatMenus.some((item) => item.path && item.path.startsWith(base))) return true

  return false
}
