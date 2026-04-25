import { Link } from 'react-router-dom'
import { 
  MagnifyingGlassIcon, 
  MapIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  BuildingLibraryIcon,
  BellAlertIcon,
  ArrowRightIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-emerald-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🦷 Open Navigator for Engagement
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered advocacy opportunity finder analyzing municipal meetings and financial documents 
            across 90,000+ jurisdictions and 3M+ nonprofits
          </p>
          
          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="relative">
              <input
                type="text"
                placeholder="Search documents, nonprofits, or locations..."
                className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent shadow-lg"
              />
              <button className="absolute right-2 top-2 bg-sky-600 text-white px-6 py-2 rounded-full hover:bg-sky-700 transition-colors">
                <MagnifyingGlassIcon className="h-6 w-6" />
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Try: "water fluoridation", "dental programs", or a city name
            </p>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-16">
            <Link 
              to="/opportunities"
              className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 group"
            >
              <div className="flex items-center justify-center mb-4">
                <div className="bg-amber-100 p-4 rounded-full">
                  <BellAlertIcon className="h-8 w-8 text-amber-600" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2 group-hover:text-sky-600">View Opportunities</h3>
              <p className="text-gray-600 text-sm">
                Discover advocacy windows based on meeting minutes and budgets
              </p>
            </Link>

            <Link 
              to="/heatmap"
              className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 group"
            >
              <div className="flex items-center justify-center mb-4">
                <div className="bg-emerald-100 p-4 rounded-full">
                  <MapIcon className="h-8 w-8 text-emerald-600" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2 group-hover:text-sky-600">Explore Heatmap</h3>
              <p className="text-gray-600 text-sm">
                Geographic visualization of policy opportunities nationwide
              </p>
            </Link>

            <Link 
              to="/nonprofits"
              className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 group"
            >
              <div className="flex items-center justify-center mb-4">
                <div className="bg-sky-100 p-4 rounded-full">
                  <BuildingLibraryIcon className="h-8 w-8 text-sky-600" />
                </div>
              </div>
              <h3 className="text-lg font-semibold mb-2 group-hover:text-sky-600">Find Nonprofits</h3>
              <p className="text-gray-600 text-sm">
                Search 3M+ organizations and IRS Form 990 financial data
              </p>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Explore the Platform</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Link to="/analytics" className="group">
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-sky-500 transition-colors">
                <ChartBarIcon className="h-10 w-10 text-sky-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-sky-600">Analytics Dashboard</h3>
                <p className="text-gray-600 mb-4">
                  Real-time statistics, charts, and insights across all monitored jurisdictions
                </p>
                <span className="text-sky-600 font-medium inline-flex items-center">
                  View Analytics <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </Link>

            <Link to="/documents" className="group">
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-sky-500 transition-colors">
                <DocumentTextIcon className="h-10 w-10 text-sky-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-sky-600">Document Explorer</h3>
                <p className="text-gray-600 mb-4">
                  Search and analyze meeting minutes, budgets, and financial reports
                </p>
                <span className="text-sky-600 font-medium inline-flex items-center">
                  Browse Documents <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </Link>

            <a 
              href="http://localhost:3000" 
              target="_blank" 
              rel="noopener noreferrer"
              className="group"
            >
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-sky-500 transition-colors">
                <BookOpenIcon className="h-10 w-10 text-sky-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-sky-600">Documentation</h3>
                <p className="text-gray-600 mb-4">
                  Comprehensive guides, API reference, and getting started tutorials
                </p>
                <span className="text-sky-600 font-medium inline-flex items-center">
                  Read Docs <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </a>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-sky-600 mb-2">90,000+</div>
              <div className="text-gray-600">Government Jurisdictions</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-emerald-600 mb-2">13,000+</div>
              <div className="text-gray-600">School Districts</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-amber-600 mb-2">3M+</div>
              <div className="text-gray-600">Nonprofit Organizations</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">100%</div>
              <div className="text-gray-600">Free & Open Data</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
