import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  MapIcon,
  DocumentTextIcon,
  BellAlertIcon,
  BuildingLibraryIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  UserGroupIcon,
  AcademicCapIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'People Finder', href: '/people', icon: UserGroupIcon },
  { name: 'Heatmap', href: '/heatmap', icon: MapIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'Causes', href: '/opportunities', icon: BellAlertIcon },
  { name: 'Nonprofits', href: '/nonprofits', icon: BuildingLibraryIcon },
  { name: 'Debate Finder', href: '/debate-grader', icon: AcademicCapIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Environment-aware URLs
  const docsUrl = import.meta.env.PROD ? '/docs' : 'http://localhost:3000'
  const apiDocsUrl = import.meta.env.PROD ? '/api/docs' : 'http://localhost:8000/docs'

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/documents?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F1F5F9' }}>
      {/* Top Header Bar */}
      <div className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
        <div className="flex items-center justify-between px-4 md:px-6 py-3">
          <div className="flex items-center gap-3">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>

            <Link to="/" className="flex items-center gap-2 md:gap-3">
              <img 
                src="/communityone_logo.jpg" 
                alt="CommunityOne Logo" 
                className="h-10 md:h-12"
              />
              <h1 className="text-lg md:text-2xl font-bold" style={{ color: '#354F52' }}>
                Open Navigator
              </h1>
            </Link>
          </div>

          {/* Global Search - Hidden on home page and mobile */}
          {location.pathname !== '/' && (
            <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-2xl mx-8">
              <div className="relative w-full">
                <input
                  type="text"
                  placeholder="Search documents, nonprofits, locations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </form>
          )}

          {/* Header Actions */}
          <div className="flex items-center gap-2 md:gap-4">
            <a
              href={docsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 md:gap-2 px-2 md:px-4 py-2 text-gray-700 hover:text-primary-600 transition-colors"
            >
              <BookOpenIcon className="h-5 w-5" />
              <span className="hidden md:inline font-medium">Docs</span>
            </a>
            <a
              href={apiDocsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-2 md:px-4 py-2 text-white rounded-lg transition-colors text-sm md:text-base"
              style={{ backgroundColor: '#354F52' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2e4346'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#354F52'}
            >
              API
            </a>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed top-16 inset-y-0 left-0 w-64 bg-white border-r border-gray-200 z-40
        transform transition-transform duration-200 ease-in-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <nav className="mt-6 px-4 overflow-y-auto h-[calc(100vh-10rem)]">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
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

        {/* Sidebar Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
          <div className="text-sm text-gray-600">
            <div className="font-medium mb-1">Data Sources</div>
            <div className="text-xs">
              • Census Bureau<br />
              • NCES Districts<br />
              • ProPublica Nonprofits
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="md:pl-64 pt-16">
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
