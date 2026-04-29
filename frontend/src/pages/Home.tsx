import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState, Fragment, useEffect } from 'react'
import { Tab } from '@headlessui/react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  BuildingLibraryIcon,
  ArrowRightIcon,
  BookOpenIcon,
  CurrencyDollarIcon,
  HomeIcon,
  TruckIcon,
  HeartIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  ScaleIcon,
  UserGroupIcon,
  CodeBracketIcon,
  BuildingOfficeIcon,
  UserIcon,
  CheckCircleIcon,
  MapPinIcon
} from '@heroicons/react/24/outline'
import AddressLookup from '../components/AddressLookup'
import { useLocation as useLocationContext } from '../contexts/LocationContext'

export default function Home() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [keyword, setKeyword] = useState('')
  const [searchScope, setSearchScope] = useState('city') // city, county, state, community (school), national
  const [selectedTab, setSelectedTab] = useState(0)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const { location, setLocation } = useLocationContext()

  const DOCS_URL = import.meta.env.PROD ? '/docs/intro' : 'http://localhost:3000/docs/intro'

  // Live search preview (type-ahead with actual results from API)
  const { data: previewResults, isLoading: previewLoading, error: previewError } = useQuery({
    queryKey: ['search-preview-home', keyword, location?.state],
    queryFn: async () => {
      console.log('🔍 [Home] Fetching preview for:', keyword, 'in state:', location?.state);
      if (!keyword || keyword.length < 2) {
        console.log('⚠️ [Home] Query too short, skipping');
        return null;
      }
      
      const url = '/api/search/';
      const params: any = {
        q: keyword,
        types: 'causes,contacts,organizations',
        limit: 3
      };
      
      // Add state filter if location is set
      if (location && location.state) {
        params.state = location.state;
        console.log('📍 [Home] Filtering by state:', location.state);
      }
      
      console.log('📤 [Home] API Request:', url, params);
      const response = await axios.get(url, { params });
      console.log('📥 [Home] API Response:', response.data);
      console.log('📊 [Home] Total results:', response.data.total_results);
      return response.data;
    },
    enabled: keyword.length >= 2 && showSuggestions,
    staleTime: 1000
  });

  // Log when preview results change
  useEffect(() => {
    console.log('🔄 [Home] Preview results updated:', {
      hasResults: !!previewResults,
      totalResults: previewResults?.total_results,
      showSuggestions,
      keyword,
      isLoading: previewLoading,
      error: previewError
    });
  }, [previewResults, showSuggestions, keyword, previewLoading, previewError]);

  // Handle tab parameter from URL
  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam === 'community') {
      setSelectedTab(1) // Switch to "Find My Local Community" tab
    }
  }, [searchParams])

  // When location is set, default to city search if currently on 'community' (placeholder)
  useEffect(() => {
    if (location && searchScope === 'community') {
      setSearchScope('city')
    }
  }, [location, searchScope])

  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setKeyword(value)
    setShowSuggestions(value.length >= 2)
  }

  const handleSelectSuggestion = (suggestion: string) => {
    setKeyword(suggestion)
    setShowSuggestions(false)
  }

  const handleViewAllCategory = (category: string) => {
    if (keyword.trim().length >= 2) {
      const params = new URLSearchParams()
      params.set('q', keyword)
      params.set('types', category)
      if (location && location.state) {
        params.set('state', location.state)
      }
      navigate(`/search?${params.toString()}`)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyword || location) {
      const params = new URLSearchParams()
      if (keyword) params.set('search', keyword)
      if (searchScope) params.set('scope', searchScope)
      
      // Add location context based on scope
      if (location) {
        if (searchScope === 'state' || searchScope === 'county' || searchScope === 'city' || searchScope === 'community') {
          params.set('state', location.state)
        }
        if (searchScope === 'county' || searchScope === 'city' || searchScope === 'community') {
          if (location.county) params.set('county', location.county)
        }
        if (searchScope === 'city' || searchScope === 'community') {
          params.set('city', location.city)
        }
      }
      
      navigate(`/documents?${params.toString()}`)
    }
  }

  const handleAddressFound = (locationData: any) => {
    setLocation({
      address: locationData.address,
      state: locationData.state,
      county: locationData.county,
      city: locationData.city,
      latitude: locationData.latitude,
      longitude: locationData.longitude,
    })
  }

  const categories = [
    { name: 'People', icon: UserGroupIcon, query: '', route: '/people' },
    { name: 'Community', icon: CodeBracketIcon, query: 'community engagement' },
    { name: 'Budget', icon: CurrencyDollarIcon, query: 'budget funding' },
    { name: 'Housing', icon: HomeIcon, query: 'housing affordable' },
    { name: 'Transport', icon: TruckIcon, query: 'transportation transit' },
    { name: 'Health', icon: HeartIcon, query: 'health dental' },
    { name: 'Education', icon: AcademicCapIcon, query: 'education school' },
    { name: 'Jobs', icon: BriefcaseIcon, query: 'employment jobs' },
    { name: 'Legal', icon: ScaleIcon, query: 'legal services' },
    { name: 'Charities', icon: BuildingLibraryIcon, query: '', route: '/nonprofits' },
  ]

  const quickSearch = (category: { query: string, route?: string }) => {
    if (category.route) {
      if (category.route.startsWith('http')) {
        window.open(category.route, '_blank')
      } else {
        navigate(category.route)
      }
    } else if (category.query) {
      navigate(`/search?q=${encodeURIComponent(category.query)}`)
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F1F5F9' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6" style={{ color: '#354F52' }}>
            Open Navigator for Engagement
          </h1>
          <p className="text-xl mb-12 max-w-3xl mx-auto" style={{ color: '#354F52' }}>
            Track what local governments and charities say, spend—and block.
            <br />
            Find leaders by name. Discover causes.{' '}
            <Link to="/jurisdictions" className="font-semibold hover:underline">925 jurisdictions</Link>.{' '}
            <Link to="/search?types=organizations" className="font-semibold hover:underline">43,726 nonprofits</Link>. All free.
          </p>

          {/* Tabbed Interface */}
          <div className="max-w-5xl mx-auto mb-8">
            <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
              <Tab.List className="flex space-x-2 rounded-xl bg-white p-2 shadow-lg mb-6">
                <Tab as={Fragment}>
                  {({ selected }) => (
                    <button
                      className={`w-full rounded-lg py-3 px-4 text-base font-medium leading-5 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        selected ? 'text-white shadow' : 'text-gray-700 hover:bg-gray-100'
                      }`}
                      style={selected ? { backgroundColor: '#354F52' } : {}}
                    >
                      🔍 Search Topics
                    </button>
                  )}
                </Tab>
                <Tab as={Fragment}>
                  {({ selected }) => (
                    <button
                      className={`w-full rounded-lg py-3 px-4 text-base font-medium leading-5 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        selected ? 'text-white shadow' : 'text-gray-700 hover:bg-gray-100'
                      }`}
                      style={selected ? { backgroundColor: '#354F52' } : {}}
                    >
                      📍 Find My Local Community
                    </button>
                  )}
                </Tab>
              </Tab.List>

              <Tab.Panels>
                {/* Search Tab */}
                <Tab.Panel>
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <form onSubmit={handleSearch}>
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
                        <div className="lg:col-span-7">
                          <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                            Search for topics, people, organizations, or causes
                          </label>
                          <div className="relative">
                            <input
                              type="text"
                              placeholder="Try: mayor, dental clinic, food bank, affordable housing..."
                              value={keyword}
                              onChange={handleKeywordChange}
                              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                              onFocus={() => {
                                if (keyword.length >= 2) {
                                  setShowSuggestions(true)
                                }
                              }}
                              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900"
                            />
                            
                            {/* Rich Preview Dropdown with Grouped Results */}
                            {showSuggestions && previewResults && previewResults.total_results > 0 && (
                              <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
                                
                                {/* Causes Section */}
                                {previewResults.results.causes.length > 0 && (
                                  <div className="border-b border-gray-200">
                                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <HeartIcon className="h-4 w-4 text-gray-500" />
                                        <span className="text-xs font-semibold text-gray-700 uppercase">Causes</span>
                                      </div>
                                      <button
                                        type="button"
                                        onClick={() => handleViewAllCategory('causes')}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.causes.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onClick={() => handleSelectSuggestion(result.title)}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors"
                                      >
                                        <HeartIcon className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                )}

                                {/* People (Contacts) Section */}
                                {previewResults.results.contacts.length > 0 && (
                                  <div className="border-b border-gray-200">
                                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <UserIcon className="h-4 w-4 text-gray-500" />
                                        <span className="text-xs font-semibold text-gray-700 uppercase">People</span>
                                      </div>
                                      <button
                                        type="button"
                                        onClick={() => handleViewAllCategory('contacts')}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.contacts.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onClick={() => handleSelectSuggestion(result.title)}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors"
                                      >
                                        <UserIcon className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                )}

                                {/* Organizations Section */}
                                {previewResults.results.organizations.length > 0 && (
                                  <div>
                                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                                      <div className="flex items-center gap-2">
                                        <BuildingOfficeIcon className="h-4 w-4 text-gray-500" />
                                        <span className="text-xs font-semibold text-gray-700 uppercase">Organizations</span>
                                      </div>
                                      <button
                                        type="button"
                                        onClick={() => handleViewAllCategory('organizations')}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.organizations.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onClick={() => handleSelectSuggestion(result.title)}
                                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors last:rounded-b-lg"
                                      >
                                        {result.metadata?.logo_url ? (
                                          <img 
                                            src={result.metadata.logo_url} 
                                            alt={`${result.title} logo`}
                                            className="h-5 w-5 rounded object-contain mt-0.5 flex-shrink-0"
                                            onError={(e) => {
                                              // Fallback to icon if image fails to load
                                              e.currentTarget.style.display = 'none';
                                              e.currentTarget.nextElementSibling?.classList.remove('hidden');
                                            }}
                                          />
                                        ) : null}
                                        <BuildingOfficeIcon className={`h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0 ${result.metadata?.logo_url ? 'hidden' : ''}`} />
                                        <div className="flex-1 min-w-0">
                                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                )}

                                {/* Footer with total results */}
                                <div className="px-4 py-2 bg-gray-50 text-center border-t border-gray-200">
                                  <button
                                    type="submit"
                                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                                  >
                                    See all {previewResults.total_results} results →
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="lg:col-span-3">
                          <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                            Search In
                          </label>
                          {location ? (
                            <div className="relative">
                              <select
                                value={searchScope}
                                onChange={(e) => setSearchScope(e.target.value)}
                                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-gray-900"
                              >
                                <option value="city">My City ({location.city})</option>
                                <option value="county">My County ({location.county || 'County'})</option>
                                <option value="state">My State ({location.state})</option>
                                <option value="community">School Board ({location.city})</option>
                                <option value="national">Nationwide</option>
                              </select>
                              <button
                                type="button"
                                onClick={() => navigate('/?tab=community')}
                                className="absolute -bottom-6 left-0 right-0 text-xs text-primary-600 hover:text-primary-700 font-medium underline flex items-center justify-center gap-1"
                              >
                                <MapPinIcon className="h-3 w-3" />
                                Change Location
                              </button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => navigate('/?tab=community')}
                              className="w-full px-4 py-3 text-lg border-2 border-primary-600 rounded-lg bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors font-semibold flex items-center justify-center gap-2"
                            >
                              <MapPinIcon className="h-5 w-5" />
                              Set Your Location First
                            </button>
                          )}
                        </div>

                        <div className="lg:col-span-2">
                          <label className="block text-left text-sm font-medium text-gray-700 mb-2 invisible">
                            Search
                          </label>
                          <button
                            type="submit"
                            className="w-full text-white px-6 py-3 rounded-lg transition-colors text-lg font-semibold flex items-center justify-center gap-2"
                            style={{ backgroundColor: '#354F52' }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2e4346'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#354F52'}
                          >
                            <MagnifyingGlassIcon className="h-6 w-6" />
                            Search
                          </button>
                        </div>
                      </div>
                    </form>
                  </div>
                </Tab.Panel>

                {/* Find My Community Tab */}
                <Tab.Panel>
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold mb-3 text-center" style={{ color: '#354F52' }}>
                      What's Happening in Your Community?
                    </h2>
                    <p className="text-gray-600 text-center mb-6">
                      Enter your address to find local organizations, city councils, county boards, school districts, and charities near you
                    </p>
                    <AddressLookup onLocationFound={handleAddressFound} />
                    
                    {/* Success message and return to search button */}
                    {location && (
                      <div className="mt-8 p-6 bg-green-50 border-2 border-green-200 rounded-xl">
                        <div className="flex items-start gap-3 mb-4">
                          <CheckCircleIcon className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-green-900 mb-1">
                              Location Set Successfully!
                            </h3>
                            <p className="text-green-700">
                              You're all set for <strong>{location.city}, {location.state}</strong>. Now you can search for topics in your community.
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => setSelectedTab(0)}
                          className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-lg font-semibold text-lg flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl"
                        >
                          <MagnifyingGlassIcon className="h-6 w-6" />
                          Search Topics in My Community
                          <ArrowRightIcon className="h-5 w-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </div>

          {/* Quick Topics */}
          <div className="max-w-5xl mx-auto mb-6">
            <p className="text-sm text-gray-600 text-center mb-3">Popular topics:</p>
            <div className="flex flex-wrap justify-center gap-3">
              {categories.map((category) => (
                <button
                  key={category.name}
                  onClick={() => quickSearch(category)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <category.icon className="h-5 w-5 text-gray-600" />
                  <span className="font-medium text-gray-700">{category.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Terms */}
          <p className="text-sm text-gray-500">
            By continuing, you agree to the{' '}
            <a href="#" className="text-primary-600 hover:underline">Terms</a>
            {' & '}
            <a href="#" className="text-primary-600 hover:underline">Privacy</a>.
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-16" style={{ backgroundColor: '#354F52' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12 text-white">Explore the Platform</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Link to="/analytics" className="group">
              <div className="bg-white border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <ChartBarIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#354F52' }}>Data & Trends</h3>
                <p className="text-gray-600 mb-4">
                  Statistics, charts, and insights. See what's happening across communities.
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
                  View Data <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </Link>

            <Link to="/documents" className="group">
              <div className="bg-white border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <DocumentTextIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#354F52' }}>Meeting Minutes</h3>
                <p className="text-gray-600 mb-4">
                  See what local governments are discussing, deciding, and spending
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
                  Browse Minutes <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </Link>

            <a href={DOCS_URL} target="_blank" rel="noopener noreferrer" className="group">
              <div className="bg-white border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 transition-colors">
                <BookOpenIcon className="h-10 w-10 text-primary-600 mb-4" />
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#354F52' }}>Learn More</h3>
                <p className="text-gray-600 mb-4">
                  Discover how to track local decisions and find charities
                </p>
                <span className="text-primary-600 font-medium inline-flex items-center">
                  Getting Started <ArrowRightIcon className="h-4 w-4 ml-2" />
                </span>
              </div>
            </a>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16" style={{ backgroundColor: '#F1F5F9' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">2,500+</div>
              <div className="text-gray-600">Causes Tracked</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-emerald-600 mb-2">15,000+</div>
              <div className="text-gray-600">Government Decisions</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-amber-600 mb-2">8 Years</div>
              <div className="text-gray-600">Historical Coverage</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-cyan-600 mb-2">5,000+</div>
              <div className="text-gray-600">Meeting Records</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: '#354F52' }}>12,000+</div>
              <div className="text-gray-600">Hours of Video</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">100%</div>
              <div className="text-gray-600">Free & Open</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
