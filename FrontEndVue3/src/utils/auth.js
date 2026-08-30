export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch (error) {
    return {}
  }
}

function normalizeRoleText(user) {
  return String(user?.role?.flag || user?.role?.name || user?.roleName || user?.role || '').toLowerCase()
}

export function isAdminUser(user = getCurrentUser()) {
  const roleText = normalizeRoleText(user)
  return roleText.includes('admin') || roleText.includes('super')
}

export function isAdminPath(path) {
  const adminOnlyPaths = ['/import-log', '/user', '/role', '/menu', '/file']
  return adminOnlyPaths.includes(path)
}
