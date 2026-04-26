import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState, useEffect, Fragment } from 'react'
import { Tab } from '@headlessui/react'
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  BuildingLibraryIcon,
  UserGroupIcon,
  MapIcon,
  BellAlertIcon,
  SparklesIcon,
  CheckCircleIcon,
  RocketLaunchIcon,
  ArrowRightIcon,
  HeartIcon,
  BookOpenIcon,
  CodeBracketIcon,
  AcademicCapIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline'
import { useLocation as useLocationContext } from '../contexts/LocationContext'
import AddressLookup from '../components/AddressLookup'

export default function HomeModern() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [keyword, setKeyword] = useState('')
  const [activeSection, setActiveSection] = useState('hero')
  const [selectedTab, setSelectedTab] = useState(0)
  const [searchScope, setSearchScope] = useState('city')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([])
  const { location, setLocation } = useLocationContext()

  // Search suggestions
  const searchSuggestions = [
    'housing', 'affordable housing', 'health', 'dental health', 'oral health',
    'education', 'school funding', 'budget', 'city budget', 'transportation',
    'public transit', 'infrastructure', 'parks', 'recreation', 'zoning',
    'development', 'public safety', 'police', 'fire department', 'water',
    'utilities', 'taxes', 'property taxes', 'employment', 'jobs',
    'economic development', 'environment', 'climate', 'sustainability',
    'waste management', 'recycling',
  ]

  // Handle tab parameter from URL
  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam === 'community') {
      setSelectedTab(1)
    }
  }, [searchParams])

  // When location is set, default to city search
  useEffect(() => {
    if (location && searchScope === 'community') {
      setSearchScope('city')
    }
  }, [location, searchScope])

  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setKeyword(value)

    if (value.length > 0) {
      const filtered = searchSuggestions.filter(suggestion =>
        suggestion.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8)
      setFilteredSuggestions(filtered)
      setShowSuggestions(filtered.length > 0)
    } else {
      setShowSuggestions(false)
    }
  }

  const handleSelectSuggestion = (suggestion: string) => {
    setKeyword(suggestion)
    setShowSuggestions(false)
  }

  // Smooth scroll to section
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      const offset = 80 // Account for sticky header
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - offset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })
    }
  }

  // Track active section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['hero', 'features', 'how-it-works', 'stats', 'get-started']
      const scrollPosition = window.scrollY + 100

      for (const section of sections) {
        const element = document.getElementById(section)
        if (element) {
          const { offsetTop, offsetHeight } = element
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(section)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyword || location) {
      const params = new URLSearchParams()
      if (keyword) params.set('search', keyword)
      if (searchScope) params.set('scope', searchScope)
      
      // Add location context based on scope
      if (location && searchScope !== 'national') {
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

  const navLinks = [
    { id: 'hero', label: 'Home' },
    { id: 'features', label: 'Features' },
    { id: 'how-it-works', label: 'How It Works' },
    { id: 'stats', label: 'Impact' },
    { id: 'get-started', label: 'Documentation' },
  ]

  const features = [
    {
      icon: UserGroupIcon,
      title: 'Find Leaders',
      description: 'Discover elected officials, decision makers, and community leaders in your area',
      link: '/people',
      color: '#354F52'
    },
    {
      icon: DocumentTextIcon,
      title: 'Meeting Minutes',
      description: 'See what local governments are discussing, deciding, and spending',
      link: '/documents',
      color: '#52796F'
    },
    {
      icon: BuildingLibraryIcon,
      title: 'Local Charities',
      description: 'Find charities and nonprofits providing services in your community',
      link: '/nonprofits',
      color: '#84A98C'
    },
    {
      icon: MapIcon,
      title: 'Map View',
      description: 'Visualize advocacy opportunities and civic engagement across regions',
      link: '/heatmap',
      color: '#4A90E2'
    },
    {
      icon: ChartBarIcon,
      title: 'Data & Trends',
      description: 'Statistics and insights across 90,000+ communities',
      link: '/analytics',
      color: '#9B59B6'
    },
    {
      icon: BellAlertIcon,
      title: 'Take Action',
      description: 'Get involved with causes and opportunities in your area',
      link: '/opportunities',
      color: '#E74C3C'
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Sticky Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <img 
                src="/communityone_logo.svg" 
                alt="CommunityOne Logo" 
                className="h-12"
              />
              <span className="text-xl font-bold" style={{ color: '#354F52' }}>
                Open Navigator
              </span>
            </Link>

            {/* Centered Navigation Links */}
            <div className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => (
                <button
                  key={link.id}
                  onClick={() => scrollToSection(link.id)}
                  className={`text-sm font-medium transition-colors ${
                    activeSection === link.id
                      ? 'text-[#354F52] border-b-2 border-[#354F52]'
                      : 'text-gray-600 hover:text-[#354F52]'
                  } pb-1`}
                >
                  {link.label}
                </button>
              ))}
            </div>

            {/* CTA Button */}
            <Link
              to="/people"
              className="px-6 py-2.5 rounded-lg text-white font-semibold hover:shadow-lg transition-all"
              style={{ backgroundColor: '#354F52' }}
            >
              Explore Now
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="hero" className="pt-32 pb-20 px-4" style={{ background: 'linear-gradient(135deg, #F1F5F9 0%, #E8EEF2 100%)' }}>
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm mb-6">
            <SparklesIcon className="h-5 w-5" style={{ color: '#354F52' }} />
            <span className="text-sm font-medium" style={{ color: '#354F52' }}>
              Civic Engagement Reimagined
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6" style={{ color: '#354F52' }}>
            Track Local Decisions.<br />
            <span className="bg-gradient-to-r from-[#52796F] to-[#84A98C] bg-clip-text text-transparent">
              Take Action.
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Follow leaders, charities, and causes in your community.<br />
            90,000+ cities • 3M+ nonprofits • 100% free
          </p>

          {/* Tabbed Search Interface */}
          <div className="max-w-5xl mx-auto mb-8">
            <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
              <Tab.List className="flex space-x-2 rounded-xl bg-white p-2 shadow-lg mb-6 max-w-2xl mx-auto">
                <Tab as={Fragment}>
                  {({ selected }) => (
                    <button
                      className={`w-full rounded-lg py-3 px-6 text-base font-medium leading-5 focus:outline-none transition-all ${
                        selected ? 'text-white shadow-md' : 'text-gray-700 hover:bg-gray-100'
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
                      className={`w-full rounded-lg py-3 px-6 text-base font-medium leading-5 focus:outline-none transition-all ${
                        selected ? 'text-white shadow-md' : 'text-gray-700 hover:bg-gray-100'
                      }`}
                      style={selected ? { backgroundColor: '#354F52' } : {}}
                    >
                      📍 Find My Community
                    </button>
                  )}
                </Tab>
              </Tab.List>

              <Tab.Panels>
                {/* Search Topics Tab */}
                <Tab.Panel>
                  <div className="bg-white rounded-2xl shadow-xl p-8">
                    <form onSubmit={handleSearch}>
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
                        <div className="lg:col-span-7">
                          <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                            What are you looking for?
                          </label>
                          <div className="relative">
                            <input
                              type="text"
                              placeholder="Try: housing, health, education, budget..."
                              value={keyword}
                              onChange={handleKeywordChange}
                              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                              onFocus={() => {
                                if (keyword.length > 0 && filteredSuggestions.length > 0) {
                                  setShowSuggestions(true)
                                }
                              }}
                              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent text-gray-900"
                            />
                            
                            {/* Autocomplete Suggestions */}
                            {showSuggestions && filteredSuggestions.length > 0 && (
                              <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
                                {filteredSuggestions.map((suggestion, index) => (
                                  <button
                                    key={index}
                                    type="button"
                                    onClick={() => handleSelectSuggestion(suggestion)}
                                    className="w-full text-left px-4 py-2 hover:bg-primary-50 text-gray-900 text-base border-b border-gray-100 last:border-b-0"
                                  >
                                    {suggestion}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="lg:col-span-3">
                          <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                            Search In
                          </label>
                          <select
                            value={searchScope}
                            onChange={(e) => {
                              const newValue = e.target.value
                              setSearchScope(newValue)
                              if (newValue === 'community' && !location) {
                                navigate('/?tab=community')
                              }
                            }}
                            className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent bg-white text-gray-900"
                          >
                            {location ? (
                              <>
                                <option value="city">My City ({location.city})</option>
                                <option value="county">My County ({location.county || 'County'})</option>
                                <option value="state">My State ({location.state})</option>
                                <option value="community">School Board ({location.city})</option>
                                <option value="national">Nationwide</option>
                              </>
                            ) : (
                              <>
                                <option value="community">Set your location first</option>
                                <option value="national">Nationwide</option>
                              </>
                            )}
                          </select>
                        </div>

                        <div className="lg:col-span-2">
                          <button
                            type="submit"
                            className="w-full text-white px-6 py-3 rounded-lg transition-all text-lg font-semibold flex items-center justify-center gap-2 hover:shadow-lg"
                            style={{ backgroundColor: '#354F52' }}
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
                  <div className="bg-white rounded-2xl shadow-xl p-8">
                    <h2 className="text-2xl font-bold mb-3 text-center" style={{ color: '#354F52' }}>
                      What's Happening in Your Community?
                    </h2>
                    <p className="text-gray-600 text-center mb-6">
                      Enter your address to find local organizations, city councils, county boards, school districts, and charities near you
                    </p>
                    <AddressLookup onLocationFound={handleAddressFound} />
                  </div>
                </Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </div>

          {/* Quick Stats */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>90,000+ Jurisdictions</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>3M+ Nonprofits</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>15,000+ Decisions Tracked</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#354F52' }}>
              Everything You Need
            </h2>
            <p className="text-xl text-gray-600">
              Powerful tools to stay informed and engaged
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Link
                key={index}
                to={feature.link}
                className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#354F52] hover:shadow-xl transition-all"
              >
                <div
                  className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                  style={{ backgroundColor: `${feature.color}15` }}
                >
                  <feature.icon className="h-7 w-7" style={{ color: feature.color }} />
                </div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {feature.description}
                </p>
                <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: feature.color }}>
                  Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4" style={{ backgroundColor: '#F1F5F9' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#354F52' }}>
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Get started in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                step: '1',
                title: 'Set Your Location',
                description: 'Tell us where you live to see local leaders, meetings, and charities',
                icon: MapIcon
              },
              {
                step: '2',
                title: 'Follow What Matters',
                description: 'Follow leaders, organizations, and causes you care about',
                icon: HeartIcon
              },
              {
                step: '3',
                title: 'Stay Informed',
                description: 'Get updates on local decisions and opportunities to take action',
                icon: BellAlertIcon
              },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div
                  className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-bold text-white"
                  style={{ backgroundColor: '#354F52' }}
                >
                  {item.step}
                </div>
                <item.icon className="h-12 w-12 mx-auto mb-4" style={{ color: '#52796F' }} />
                <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                  {item.title}
                </h3>
                <p className="text-gray-600 text-lg">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="stats" className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#354F52' }}>
              Our Impact
            </h2>
            <p className="text-xl text-gray-600">
              Real numbers from real communities
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { value: '90,000+', label: 'Cities & Counties', color: '#354F52' },
              { value: '3M+', label: 'Nonprofits Tracked', color: '#52796F' },
              { value: '15,000+', label: 'Decisions Analyzed', color: '#84A98C' },
              { value: '50 States', label: 'Nationwide Coverage', color: '#4A90E2' },
              { value: '13,000+', label: 'School Districts', color: '#6B8E23' },
              { value: '500K+', label: 'Meeting Minutes', color: '#8B4513' },
              { value: '$2T+', label: 'Budget Dollars Tracked', color: '#DC143C' },
              { value: '100K+', label: 'Public Officials', color: '#9370DB' },
              { value: '100%', label: 'Free & Open Source', color: '#2E8B57' },
            ].map((stat, index) => (
              <div key={index} className="text-center p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white shadow-md hover:shadow-xl transition-shadow">
                <div className="text-5xl font-bold mb-3" style={{ color: stat.color }}>
                  {stat.value}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Documentation Section */}
      <section id="get-started" className="py-20 px-4" style={{ background: 'linear-gradient(135deg, #354F52 0%, #52796F 100%)' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <BookOpenIcon className="h-16 w-16 mx-auto mb-6 text-white" />
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
              Documentation & Resources
            </h2>
            <p className="text-xl text-white/90">
              Choose your path based on your role and technical expertise
            </p>
          </div>

          {/* Documentation Tiles */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Getting Started - Everyone */}
            <a
              href="http://localhost:3000/docs/intro"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <RocketLaunchIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                🚀 Getting Started
              </h3>
              <p className="text-gray-600 mb-4">
                New here? Start with our quick introduction and dashboard overview.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                For Everyone →
              </div>
            </a>

            {/* Policy Makers & Advocates - Non-Technical */}
            <a
              href="http://localhost:3000/docs/category/for-policy-makers--advocates"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <AcademicCapIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                📊 Policy Makers
              </h3>
              <p className="text-gray-600 mb-4">
                Case studies, data insights, and how to use the platform for advocacy.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                Non-Technical →
              </div>
            </a>

            {/* Developers & Technical Users */}
            <a
              href="http://localhost:3000/docs/category/for-developers--technical-users"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <CodeBracketIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                🛠️ Developers
              </h3>
              <p className="text-gray-600 mb-4">
                Setup guides, API docs, deployment instructions, and integrations.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                Technical →
              </div>
            </a>

            {/* Full Documentation */}
            <a
              href="http://localhost:3000/docs/intro"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <CommandLineIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                📚 Full Docs
              </h3>
              <p className="text-gray-600 mb-4">
                Complete documentation including data sources, guides, and more.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                Browse All →
              </div>
            </a>
          </div>

          {/* Quick Actions Below */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12 max-w-4xl mx-auto">
            <Link
              to="/people"
              className="px-8 py-4 bg-white rounded-xl font-semibold hover:shadow-xl transition-all text-center"
              style={{ color: '#354F52' }}
            >
              Browse Leaders →
            </Link>
            <Link
              to="/nonprofits"
              className="px-8 py-4 bg-white/10 border-2 border-white rounded-xl text-white font-semibold hover:bg-white/20 transition-all text-center"
            >
              Explore Charities →
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <img 
              src="/communityone_logo.svg" 
              alt="CommunityOne Logo" 
              className="h-10 opacity-90"
            />
            <span className="text-xl font-bold">Open Navigator</span>
          </div>
          <p className="text-gray-400 mb-6">
            Empowering communities through transparency and engagement
          </p>
          <div className="flex justify-center gap-8 text-sm text-gray-400">
            <Link to="/docs" className="hover:text-white transition-colors">Documentation</Link>
            <Link to="/api/docs" className="hover:text-white transition-colors">API</Link>
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
          </div>
          <p className="text-gray-500 text-sm mt-6">
            © 2026 CommunityOne. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
