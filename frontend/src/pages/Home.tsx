import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { 
  MagnifyingGlassIcon, 
  MapIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  BuildingLibraryIcon,
  BellAlertIcon,
  ArrowRightIcon,
  BookOpenIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  HomeIcon,
  TruckIcon,
  HeartIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  ScaleIcon
} from '@heroicons/react/24/outline'

export default function Home() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')
  const [location, setLocation] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyword || location) {
      const params = new URLSearchParams()
      if (keyword) params.set('search', keyword)
      if (location) params.set('location', location)
      navigate(`/documents?${params.toString()}`)
    }
  }

  const categories = [
    { name: 'Budget', icon: CurrencyDollarIcon, query: 'budget funding' },
    { name: 'Housing', icon: HomeIcon, query: 'housing affordable' },
    { name: 'Transport', icon: TruckIcon, query: 'transportation transit' },
    { name: 'Health', icon: HeartIcon, query: 'health dental' },
    { name: 'Education', icon: AcademicCapIcon, query: 'education school' },
    { name: 'Jobs', icon: BriefcaseIcon, query: 'employment jobs' },
    { name: 'Legal', icon: ScaleIcon, query: 'legal services' },
    { name: 'Nonprofits', icon: BuildingLibraryIcon, query: '' },
  ]

  const quickSearch = (query: string) => {
    if (query) {
      navigate(`/documents?search=${encodeURIComponent(query)}`)
    } else {
      navigate('/nonprofits')
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F0F4F5' }}>
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <div className="flex items-center justify-center gap-4 mb-6">
            <img 
              src="/communityone_logo.jpg" 
              alt="CommunityOne Logo" 
              className="h-20 w-auto"
            />
            <h1 className="text-5xl font-bold text-gray-900">
              Open Navigator for Engagement
            </h1>
          </div>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Track what local governments and nonprofits say and spend.
            <br />
            90,000+ cities. 3M+ nonprofits. All free.
          </p>
          
          {/* Two-Part Search */}
          <form onSubmit={handleSearch} className="max-w-5xl mx-auto mb-8">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
                {/* What are you looking for? */}
                <div className="lg:col-span-7">
                  <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                    What are you looking for today?
                  </label>
                  <input
                    type="text"
                    placeholder="Enter a topic, keyword, or program name..."
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Where? */}
                <div className="lg:col-span-3">
                  <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                    Where?
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="City, County, or ZIP"
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full px-4 py-3 pl-10 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <MapPinIcon className="absolute left-3 top-3.5 h-6 w-6 text-gray-400" />
                  </div>
                </div>

                {/* Find Button */}
                <div className="lg:col-span-2">
                  <button
                    type="submit"
                    className="w-full bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors text-lg font-semibold flex items-center justify-center gap-2"
                  >
                    <MagnifyingGlassIcon className="h-6 w-6" />
                    Find
                  </button>
                </div>
              </div>
            </div>
          </form>

          {/* Category Quick Buttons */}
          <div className="max-w-5xl mx-auto mb-6">
            <div className="flex flex-wrap justify-center gap-3">
              {categories.map((category) => (
                <button
                  key={category.name}
                  onClick={() => quickSearch(category.query)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <category.icon className="h-5 w-5 text-gray-600" />
                  <span className="font-medium text-gray-700">{category.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Terms Note */}
          <p className="text-sm text-gray-500">
            By continuing, you agree to the{' '}
            <a href="#" className="text-primary-600 hover:underline">Terms</a>
            {' & '}
            <a href="#" className="text-primary-600 hover:underline">Privacy</a>.
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Explore the Platform</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Link to="/analytics" className="group">
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <ChartBarIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600">Analytics Dashboard</h3>
                <p className="text-gray-600 mb-4">
                  Real-time statistics, charts, and insights across all monitored jurisdictions
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
                  View Analytics <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </Link>

            <Link to="/documents" className="group">
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <DocumentTextIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600">Document Explorer</h3>
                <p className="text-gray-600 mb-4">
                  Search and analyze meeting minutes, budgets, and financial reports
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
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
              <div className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <BookOpenIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-600">Documentation</h3>
                <p className="text-gray-600 mb-4">
                  Comprehensive guides, API reference, and getting started tutorials
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
                  Read Docs <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </a>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16" style={{ backgroundColor: '#F0F4F5' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">90,000+</div>
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
