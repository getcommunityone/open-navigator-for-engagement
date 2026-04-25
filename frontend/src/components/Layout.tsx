import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  HomeIcon,
  MapIcon,
  DocumentTextIcon,
  BellAlertIcon,
  BuildingLibraryIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Heatmap', href: '/heatmap', icon: MapIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'Opportunities', href: '/opportunities', icon: BellAlertIcon },
  { name: 'Nonprofits', href: '/nonprofits', icon: BuildingLibraryIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center justify-center border-b border-gray-200">
          <h1 className="text-xl font-bold text-primary-600">
            🦷 Open Navigator
          </h1>
        </div>
        
        <nav className="mt-6 px-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors
                  ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <item.icon className="h-6 w-6" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <header className="bg-white shadow-sm">
          <div className="mx-auto max-w-7xl px-8 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-gray-900">
                {navigation.find((item) => item.href === location.pathname)?.name || 'Dashboard'}
              </h2>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  Last updated: {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-8 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
