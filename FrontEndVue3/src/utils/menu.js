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

export function hasRoutePermission(path) {
  const menus = JSON.parse(localStorage.getItem('menus') || '[]')
  if (!menus.length) {
    return true
  }

  const flatMenus = flattenMenus(menus)
  // Exact match or pagePath match
  if (flatMenus.some((item) => item.path === path || `/${item.pagePath || ''}` === path)) return true

  // Always allow track-related routes (track list / track map)
  if (path && path.startsWith('/track')) return true

  // Allow navigation to child routes under a menu path, e.g. /track/map/1 under /track
  const segments = (path || '').split('/')
  const base = segments.length > 1 ? `/${segments[1]}` : path
  if (flatMenus.some((item) => item.path && item.path.startsWith(base))) return true

  return false
}
