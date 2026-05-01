import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState, useEffect, Fragment, useRef } from 'react'
import { Tab } from '@headlessui/react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
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
  CommandLineIcon,
  Bars3Icon,
  XMarkIcon,
  BuildingOfficeIcon,
  UserIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline'
import { useLocation as useLocationContext } from '../contexts/LocationContext'
import AddressLookup from '../components/AddressLookup'

export default function HomeModern() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [keyword, setKeyword] = useState('')
  const [debouncedKeyword, setDebouncedKeyword] = useState('')
  const [activeSection, setActiveSection] = useState('hero')
  const [selectedTab, setSelectedTab] = useState(0)
  const [searchScope, setSearchScope] = useState('city')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { location, setLocation} = useLocationContext()
  const searchContainerRef = useRef<HTMLDivElement>(null)

  // Debounce keyword input (300ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      console.log('⏱️ [HomeModern] Debounced keyword update:', keyword);
      setDebouncedKeyword(keyword);
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [keyword]);

  // Close suggestions dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    if (showSuggestions) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showSuggestions]);

  // Environment-aware URLs for docs and API
  // In development: Docusaurus on localhost:3000/docs, API on localhost:8000
  // In production (HF Spaces): Served via nginx at /docs/ and /api/
  let docsBaseUrl = import.meta.env.VITE_DOCS_URL || 
    (import.meta.env.DEV ? 'http://localhost:3000/docs' : '/docs')
  let apiBaseUrl = import.meta.env.VITE_API_URL || 
    (import.meta.env.DEV ? 'http://localhost:8000' : '')

  // Fix mixed content: Force HTTPS if page is HTTPS and URLs start with http://
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    if (docsBaseUrl.startsWith('http://')) {
      docsBaseUrl = docsBaseUrl.replace('http://', 'https://')
    }
    if (apiBaseUrl.startsWith('http://')) {
      apiBaseUrl = apiBaseUrl.replace('http://', 'https://')
    }
  }

  // Fetch all stats at once for all scopes (city, county, state) - more efficient
  const { data: allStatsData, isLoading: statsLoading } = useQuery({
    queryKey: ['platform-stats-all', location?.state, location?.county, location?.city],
    queryFn: async () => {
      if (!location || !location.state) {
        console.log('📊 [HomeModern] No location set, skipping stats fetch');
        return null;
      }
      
      console.log('📊 [HomeModern] Fetching stats for location:', location);
      
      // Fetch stats for all scopes in parallel
      const [cityStats, countyStats, stateStats] = await Promise.all([
        // City stats
        location.city 
          ? api.get('/stats', { params: { state: location.state, county: location.county, city: location.city } })
              .then(res => {
                console.log('📊 [HomeModern] City stats:', res.data.data);
                return res.data.data;
              })
              .catch(err => {
                console.error('❌ [HomeModern] City stats error:', err);
                return null;
              })
          : Promise.resolve(null),
        // County stats
        location.county 
          ? api.get('/stats', { params: { state: location.state, county: location.county } })
              .then(res => {
                console.log('📊 [HomeModern] County stats:', res.data.data);
                return res.data.data;
              })
              .catch(err => {
                console.error('❌ [HomeModern] County stats error:', err);
                return null;
              })
          : Promise.resolve(null),
        // State stats - ALWAYS fetch if we have a state
        api.get('/stats', { params: { state: location.state } })
          .then(res => {
            console.log('📊 [HomeModern] State stats:', res.data.data);
            return res.data.data;
          })
          .catch(err => {
            console.error('❌ [HomeModern] State stats error:', err);
            return null;
          })
      ]);
      
      const result = {
        city: cityStats,
        county: countyStats,
        state: stateStats,
        community: cityStats // Use city stats for community/school board
      };
      
      console.log('📊 [HomeModern] All stats loaded:', result);
      return result;
    },
    enabled: !!(location && location.state), // Only fetch when we have at least a state
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
    refetchOnWindowFocus: false
  });

  // Get the stats for the currently selected scope
  const statsData = allStatsData?.[searchScope as keyof typeof allStatsData];
  
  console.log('📊 [HomeModern] Current scope:', searchScope, 'Stats data:', statsData, 'Loading:', statsLoading);

  // Live search preview (type-ahead with actual results from API)
  const { data: previewResults, isLoading: previewLoading, error: previewError } = useQuery({
    queryKey: ['search-preview-home', debouncedKeyword, location?.state],
    queryFn: async () => {
      console.log('🔍 [HomeModern] Fetching preview for:', debouncedKeyword, 'in state:', location?.state);
      if (!debouncedKeyword || debouncedKeyword.length < 2) {
        console.log('⚠️ [HomeModern] Query too short, skipping');
        return null;
      }
      
      const url = '/search/';
      const params: any = {
        q: debouncedKeyword,
        types: 'causes,contacts,organizations',
        limit: 3
      };
      
      // Add state filter if location is set
      if (location && location.state) {
        params.state = location.state;
        console.log('📍 [HomeModern] Filtering by state:', location.state);
      }
      
      console.log('📤 [HomeModern] API Request:', url, params);
      try {
        const response = await api.get(url, { params });
        console.log('📥 [HomeModern] API Response:', response.data);
        console.log('📊 [HomeModern] Total results:', response.data.total_results);
        console.log('🎯 [HomeModern] Causes:', response.data.results.causes.length);
        console.log('👥 [HomeModern] Contacts:', response.data.results.contacts.length);
        console.log('🏢 [HomeModern] Organizations:', response.data.results.organizations.length);
        return response.data;
      } catch (error: any) {
        console.error('❌ [HomeModern] API Error:', error);
        console.error('❌ [HomeModern] Error message:', error.message);
        console.error('❌ [HomeModern] Error response:', error.response?.data);
        console.error('❌ [HomeModern] Error status:', error.response?.status);
        throw error;
      }
    },
    enabled: debouncedKeyword.length >= 2 && showSuggestions,
    staleTime: 1000, // Cache for 1 second to avoid excessive requests
    retry: false // Don't retry failed requests to see errors immediately
  });

  // Log when preview results change
  useEffect(() => {
    console.log('🔄 [HomeModern] Preview results updated:', {
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
      setSelectedTab(1)
    }
  }, [searchParams])

  // Handle scope parameter from URL (when navigating from jurisdiction cards)
  useEffect(() => {
    const scopeParam = searchParams.get('scope')
    if (scopeParam && ['city', 'county', 'state', 'community', 'national'].includes(scopeParam)) {
      setSearchScope(scopeParam)
      setSelectedTab(0) // Switch to search tab
    }
  }, [searchParams])

  // When location is set, default to city search
  useEffect(() => {
    if (location && searchScope === 'community') {
      setSearchScope('city')
    }
  }, [location, searchScope])

  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    console.log('⌨️ [HomeModern] Keyword changed:', value);
    setKeyword(value);
    setShowSuggestions(value.length >= 2);
    console.log('👁️ [HomeModern] Show suggestions:', value.length >= 2);
  }

  const handleSelectSuggestion = (suggestion: string) => {
    setKeyword(suggestion)
    setShowSuggestions(false)
    
    // Navigate to search results with the selected suggestion
    const params = new URLSearchParams()
    params.set('q', suggestion)
    if (location && location.state) {
      params.set('state', location.state)
    }
    navigate(`/search?${params.toString()}`)
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
      if (keyword) params.set('q', keyword)
      
      // Add location context
      if (location && location.state) {
        params.set('state', location.state)
      }
      
      navigate(`/search?${params.toString()}`)
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
    { id: 'contact', label: 'Contact' },
  ]

  const features = [
    {
      icon: DocumentTextIcon,
      title: 'Policy Decisions',
      description: 'Track 500K+ meeting pages with decision analysis, deferral patterns, and stakeholder positions',
      link: '/documents',
      color: '#354F52'
    },
    {
      icon: ChartBarIcon,
      title: 'Budget Analysis',
      description: 'Compare budget rhetoric to reality with $2T+ in tracked spending and delta analysis',
      link: '/analytics',
      color: '#52796F'
    },
    {
      icon: UserGroupIcon,
      title: 'Elected Officials',
      description: 'Follow 362 officials across 925 jurisdictions with voting records and decision patterns',
      link: '/people',
      color: '#84A98C'
    },
    {
      icon: MapIcon,
      title: 'Policy Map',
      description: 'Track state legislation and bills across all sessions. Search 13,000+ bills by topic and status',
      link: '/policy-map',
      color: '#4A90E2'
    },
    {
      icon: BuildingLibraryIcon,
      title: 'Nonprofits & Churches',
      description: '43,726 nonprofits including 4,372 churches with financial data from 5 states',
      link: '/nonprofits',
      color: '#9B59B6'
    },
    {
      icon: BellAlertIcon,
      title: 'Fact-Checking',
      description: 'Verify claims with integrated PolitiFact, FactCheck.org, and Google Fact Check data',
      link: '/debate-grader',
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

            {/* Desktop Navigation Links */}
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

            {/* Desktop CTA Button */}
            <Link
              to="/explore"
              className="hidden md:block px-6 py-2.5 rounded-lg text-white font-semibold hover:shadow-lg transition-all"
              style={{ backgroundColor: '#354F52' }}
            >
              Explore Now
            </Link>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-4 py-3 space-y-1">
              {navLinks.map((link) => (
                <button
                  key={link.id}
                  onClick={() => {
                    scrollToSection(link.id)
                    setMobileMenuOpen(false)
                  }}
                  className={`block w-full text-left px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                    activeSection === link.id
                      ? 'bg-[#354F52] text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {link.label}
                </button>
              ))}
              <Link
                to="/explore"
                className="block w-full text-center px-4 py-3 mt-2 rounded-lg text-white font-semibold"
                style={{ backgroundColor: '#354F52' }}
                onClick={() => setMobileMenuOpen(false)}
              >
                Explore Now
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section id="hero" className="pt-32 pb-20 px-4" style={{ background: 'linear-gradient(135deg, #F1F5F9 0%, #E8EEF2 100%)' }}>
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm mb-6 animate-[slideUp_0.6s_ease-out]">
            <SparklesIcon className="h-5 w-5" style={{ color: '#354F52' }} />
            <span className="text-sm font-medium" style={{ color: '#354F52' }}>
              The open path to everything local
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 animate-[slideUp_0.8s_ease-out_0.2s_both]" style={{ color: '#354F52' }}>
            Track Local Decisions.<br />
            <span className="bg-gradient-to-r from-[#52796F] to-[#84A98C] bg-clip-text text-transparent">
              Take Action.
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto animate-[slideUp_0.8s_ease-out_0.4s_both]">
            Follow leaders, charities, and causes in your community.<br />
            {/* Show search-filtered counts when actively searching, otherwise show location stats */}
            {keyword.length >= 2 && previewResults && previewResults.total_results > 0 ? (
              <>
                <span className="font-semibold text-[#52796F]">
                  {previewResults.total_results.toLocaleString()} result{previewResults.total_results !== 1 ? 's' : ''}
                </span>
                {' matching "'}
                <span className="font-bold text-[#354F52]">{keyword}</span>
                {'"'}
                {location && (
                  <>
                    {' in '}
                    <span className="font-semibold text-[#52796F]">
                      {location.city || location.county || location.state}
                    </span>
                  </>
                )}
              </>
            ) : keyword.length >= 2 && previewResults && previewResults.total_results === 0 ? (
              <>
                <span className="text-gray-500">
                  No results found for "{keyword}"
                  {location && ` in ${location.city || location.county || location.state}`}
                </span>
              </>
            ) : statsData ? (
              // Show stats for any level (state, county, city, community)
              (statsData.level === 'state' || statsData.level === 'county' || statsData.level === 'city' || statsData.level === 'community') ? (
                <>
                  {/* Jurisdictions link */}
                  {statsData.level === 'city' && statsData.jurisdictions_breakdown ? (
                    <Link
                      to={`/jurisdictions?state=${statsData.state}&jurisdiction_details=${encodeURIComponent(JSON.stringify(statsData.jurisdictions_breakdown))}`}
                      className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                    >
                      {statsData.jurisdictions_display} jurisdictions
                    </Link>
                  ) : (
                    <Link 
                      to={`/jurisdictions?state=${statsData.state}${statsData.county ? `&county=${encodeURIComponent(statsData.county)}` : ''}${statsData.city ? `&city=${encodeURIComponent(statsData.city)}` : ''}`}
                      className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                    >
                      {statsData.jurisdictions_display} jurisdictions
                    </Link>
                  )}
                  {' • '}
                  {/* Nonprofits link */}
                  <Link 
                    to={`/search?types=organizations&state=${statsData.state}${statsData.county ? `&county=${encodeURIComponent(statsData.county)}` : ''}${statsData.city ? `&city=${encodeURIComponent(statsData.city)}` : ''}`}
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.nonprofits_display} nonprofits
                  </Link>
                  {' • '}
                  {/* Contacts link */}
                  <Link 
                    to={`/search?types=contacts&state=${statsData.state}${statsData.county ? `&county=${encodeURIComponent(statsData.county)}` : ''}${statsData.city ? `&city=${encodeURIComponent(statsData.city)}` : ''}`}
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.contacts_display} leaders
                  </Link>
                  {' • '}
                  {/* Causes link */}
                  <Link 
                    to={`/search?types=causes&state=${statsData.state}${statsData.county ? `&county=${encodeURIComponent(statsData.county)}` : ''}${statsData.city ? `&city=${encodeURIComponent(statsData.city)}` : ''}`}
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.causes_display} causes
                  </Link>
                  {' in '}{statsData.location} • 100% free
                </>
              ) : (
                // Fallback for unknown level or no location data
                <>
                  <Link 
                    to={`/jurisdictions${statsData.state ? `?state=${statsData.state}` : ''}`}
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.jurisdictions_display} jurisdictions
                  </Link>
                  {' • '}
                  <Link 
                    to="/search?types=organizations"
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.nonprofits_display} nonprofits
                  </Link>
                  {' • '}
                  <Link 
                    to="/search?types=contacts"
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.contacts_display} leaders
                  </Link>
                  {' • '}
                  <Link 
                    to="/search?types=causes"
                    className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                  >
                    {statsData.causes_display} causes
                  </Link>
                  {' • 100% free'}
                </>
              )
            ) : (
              <>
                <Link 
                  to="/jurisdictions"
                  className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                >
                  925 jurisdictions
                </Link>
                {' • '}
                <Link 
                  to="/search?types=organizations"
                  className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                >
                  43,726 nonprofits
                </Link>
                {' • '}
                <Link 
                  to="/search?types=contacts"
                  className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                >
                  10,000+ leaders
                </Link>
                {' • '}
                <Link 
                  to="/search?types=causes"
                  className="font-semibold text-[#52796F] hover:text-[#354F52] no-underline hover:underline hover:decoration-2 transition-all duration-200"
                >
                  650+ causes
                </Link>
                {' • 100% free'}
              </>
            )}
          </p>

          {/* Tabbed Search Interface */}
          <div className="relative z-20 max-w-5xl mx-auto mb-8 animate-[slideUp_0.8s_ease-out_0.6s_both]">
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
                  <div className="relative z-10 bg-white rounded-2xl shadow-xl p-8">
                    <form onSubmit={handleSearch}>
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
                        <div className="lg:col-span-7">
                          <label className="block text-left text-sm font-medium text-gray-900 mb-2">
                            Search for topics, people, organizations, or causes
                          </label>
                          <div className="relative" ref={searchContainerRef}>
                            <input
                              type="text"
                              placeholder="Try: mayor, dental clinic, food bank, affordable housing..."
                              value={keyword}
                              onChange={handleKeywordChange}
                              onFocus={() => {
                                if (keyword.length >= 2) {
                                  setShowSuggestions(true)
                                }
                              }}
                              className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent bg-white text-gray-900"
                            />
                            
                            {/* Loading State - Shows immediately when typing */}
                            {showSuggestions && !previewResults && !previewError && (
                              <div className="absolute z-50 w-full mt-2 border-2 border-gray-300 rounded-lg shadow-2xl" style={{ backgroundColor: '#ffffff' }}>
                                <div className="px-4 py-8 flex flex-col items-center justify-center gap-3">
                                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                                  <p className="text-sm text-gray-600">Searching...</p>
                                </div>
                              </div>
                            )}

                            {/* Error Message */}
                            {showSuggestions && previewError && (
                              <div className="absolute z-50 w-full mt-2 border-2 border-red-300 rounded-lg shadow-2xl" style={{ backgroundColor: '#FEF2F2' }}>
                                <div className="px-4 py-3 flex items-start gap-3">
                                  <svg className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                  </svg>
                                  <div className="flex-1">
                                    <h3 className="text-sm font-semibold text-red-800 mb-1">Unable to Load Results</h3>
                                    <p className="text-sm text-red-600">We're having trouble connecting to our search service. Please try again in a moment.</p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Rich Preview Dropdown with Grouped Results */}
                            {showSuggestions && !previewError && previewResults && previewResults.total_results > 0 && (
                              <div className="absolute z-50 w-full mt-2 border-2 border-gray-300 rounded-lg shadow-2xl max-h-96 overflow-y-auto" style={{ backgroundColor: '#ffffff' }}>
                                
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
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleViewAllCategory('causes');
                                        }}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.causes.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleSelectSuggestion(result.title);
                                        }}
                                        className="w-full text-left px-4 py-2 bg-white hover:bg-gray-50 flex items-start gap-3 transition-colors"
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
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleViewAllCategory('contacts');
                                        }}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.contacts.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleSelectSuggestion(result.title);
                                        }}
                                        className="w-full text-left px-4 py-2 bg-white hover:bg-gray-50 flex items-start gap-3 transition-colors"
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
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleViewAllCategory('organizations');
                                        }}
                                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                                      >
                                        View All
                                      </button>
                                    </div>
                                    {previewResults.results.organizations.slice(0, 3).map((result: any, idx: number) => (
                                      <button
                                        key={idx}
                                        type="button"
                                        onMouseDown={(e) => {
                                          e.preventDefault();
                                          handleSelectSuggestion(result.title);
                                        }}
                                        className="w-full text-left px-4 py-2 bg-white hover:bg-gray-50 flex items-start gap-3 transition-colors last:rounded-b-lg"
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

                            {/* No Results State */}
                            {showSuggestions && !previewError && !previewLoading && previewResults && previewResults.total_results === 0 && (
                              <div className="absolute z-50 w-full mt-2 border-2 border-gray-300 rounded-lg shadow-2xl" style={{ backgroundColor: '#ffffff' }}>
                                <div className="px-4 py-6 text-center">
                                  <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                                  <p className="text-sm font-medium text-gray-900 mb-1">No results found</p>
                                  <p className="text-xs text-gray-600">Try different keywords or check your spelling</p>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="lg:col-span-3">
                          <label className="block text-left text-sm font-medium text-gray-900 mb-2">
                            Search In
                          </label>
                          {location ? (
                            <div className="relative">
                              <select
                                value={searchScope}
                                onChange={(e) => setSearchScope(e.target.value)}
                                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent bg-white text-gray-900"
                              >
                                <option value="city" className="text-gray-900 bg-white">My City ({location.city})</option>
                                <option value="county" className="text-gray-900 bg-white">My County ({location.county || 'County'})</option>
                                <option value="state" className="text-gray-900 bg-white">My State ({location.state})</option>
                                <option value="community" className="text-gray-900 bg-white">School Board ({location.city})</option>
                              </select>
                              <button
                                type="button"
                                onClick={() => setSelectedTab(1)}
                                className="absolute -bottom-6 left-0 right-0 text-xs text-primary-600 hover:text-primary-700 font-medium underline flex items-center justify-center gap-1"
                              >
                                <MapIcon className="h-3 w-3" />
                                Change Location
                              </button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => setSelectedTab(1)}
                              className="w-full px-4 py-3 text-lg border-2 border-[#354F52] rounded-lg bg-[#E8EFEA] text-[#354F52] hover:bg-[#d9e5db] transition-colors font-semibold flex items-center justify-center gap-2"
                            >
                              <MapIcon className="h-5 w-5" />
                              Set Your Location First
                            </button>
                          )}
                        </div>

                        <div className="lg:col-span-2">
                          <label className="block text-left text-sm font-medium text-gray-900 mb-2 invisible">
                            Search
                          </label>
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

          {/* Quick Stats */}
          <div className="relative z-[1] flex flex-wrap justify-center gap-8 text-sm text-gray-600 animate-[slideUp_0.8s_ease-out_0.8s_both]">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>{statsData?.jurisdictions_display || '90,000+'} Jurisdictions</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>{statsData?.nonprofits_display || '43,726'} Nonprofits</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span>{statsData?.meetings_display || '500K+'} Meetings Analyzed</span>
            </div>
          </div>
        </div>
      </section>

      {/* Jurisdiction Discovery CTA */}
      <section id="jurisdictions" className="py-20 px-4 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <MapIcon className="h-16 w-16 mx-auto mb-6" style={{ color: '#354F52' }} />
            <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#354F52' }}>
              Explore Jurisdictions
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Search and filter through 32,000+ cities, counties, and school districts across all 50 states.
              View meeting schedules, discovery status, and available data sources.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/jurisdictions"
                className="inline-flex items-center justify-center px-8 py-4 rounded-lg text-white font-semibold transition-all hover:shadow-lg"
                style={{ backgroundColor: '#354F52' }}
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                Browse Jurisdictions
              </Link>
              <a
                href="#contact"
                className="inline-flex items-center justify-center px-8 py-4 rounded-lg bg-white border-2 text-[#354F52] font-semibold transition-all hover:bg-gray-50"
                style={{ borderColor: '#354F52' }}
              >
                Request Coverage
              </a>
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
              Powerful tools to stay informed and engaged with the most impactful details
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
              {statsData?.level === 'state' ? `Our Impact in ${statsData.location}` : 'Our Impact'}
            </h2>
            <p className="text-xl text-gray-600">
              {statsData?.level === 'state' ? 
                `Real numbers for ${statsData.location} from live data tables` :
                `Real numbers from real data tables`
              }
              {statsData?.last_updated && (
                <span className="text-sm text-gray-500 ml-2">
                  (updated {new Date(statsData.last_updated).toLocaleDateString()})
                </span>
              )}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {(() => {
              const stats = [
                { 
                  value: statsData?.jurisdictions_display || '925', 
                  label: 'Jurisdictions Tracked', 
                  description: 'Cities, counties, states, and tribal governments', 
                  color: '#354F52' 
                },
                { 
                  value: statsData?.nonprofits_display || '43,726', 
                  label: 'Nonprofits & Churches', 
                  description: statsData ? `${statsData.states_with_data} states with full IRS BMF data` : '5 states with full IRS BMF data', 
                  color: '#52796F' 
                },
                { 
                  value: statsData?.meetings_display || '6,913', 
                  label: 'Meeting Pages Analyzed', 
                  description: 'AI-extracted decisions and budget items', 
                  color: '#84A98C' 
                },
                { 
                  value: statsData?.budget_tracked || 'N/A', 
                  label: 'Budget Dollars', 
                  description: 'Real-time tracking and delta analysis', 
                  color: '#4A90E2' 
                },
                { 
                  value: statsData?.contacts_display || '362', 
                  label: 'Elected Officials', 
                  description: 'Voting records and decision patterns', 
                  color: '#9B59B6' 
                },
                { 
                  value: statsData?.churches || '4,372', 
                  label: 'Churches & Congregations', 
                  description: 'Community-based organizations mapped', 
                  color: '#6B8E23' 
                },
                { 
                  value: statsData?.policy_decisions || 'N/A', 
                  label: 'Policy Decisions', 
                  description: 'With deferral tracking and stakeholder positions', 
                  color: '#DC143C' 
                },
                { 
                  value: statsData?.school_districts_display || '306', 
                  label: 'School Districts', 
                  description: 'NCES-validated educational boundaries', 
                  color: '#8B4513' 
                },
                { 
                  value: statsData?.states_with_data ? `${statsData.states_with_data} State${statsData.states_with_data !== 1 ? 's' : ''}` : '5 States', 
                  label: 'State Coverage', 
                  description: 'Including territories and tribal nations', 
                  color: '#2E8B57' 
                },
                { 
                  value: statsData?.grant_opportunities || '1,000s', 
                  label: 'Grant Opportunities', 
                  description: 'Federal, state, and foundation funding', 
                  color: '#FF6B6B' 
                },
                { 
                  value: statsData?.fact_checks || 'N/A', 
                  label: 'Fact-Checked Claims', 
                  description: 'PolitiFact, FactCheck.org integration', 
                  color: '#4ECDC4' 
                },
                { 
                  value: '100%', 
                  label: 'Free & Open Source', 
                  description: 'MIT License, HuggingFace datasets', 
                  color: '#95E1D3' 
                },
              ];
              
              return stats.map((stat, index) => (
                <div key={index} className="text-center p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white shadow-md hover:shadow-xl transition-shadow group">
                  <div className="text-5xl font-bold mb-2 group-hover:scale-110 transition-transform" style={{ color: stat.color }}>
                    {stat.value}
                  </div>
                  <div className="text-gray-800 font-semibold mb-1">
                    {stat.label}
                  </div>
                  <div className="text-sm text-gray-600">
                    {stat.description}
                  </div>
                </div>
              ));
            })()}
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
            {/* Getting Started - Everyone */}
            <a
              href={`${docsBaseUrl}/intro`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <RocketLaunchIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                Getting Started
              </h3>
              <p className="text-gray-600 mb-4">
                New here? Start with our quick introduction and dashboard overview.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                For Everyone →
              </div>
            </a>

            {/* Families & Individuals */}
            <a
              href={`${docsBaseUrl}/for-families`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <HeartIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                Families & Individuals
              </h3>
              <p className="text-gray-600 mb-4">
                Community events, voter registration, services, and how to engage locally.
              </p>
              <div className="text-sm font-semibold" style={{ color: '#354F52' }}>
                Community Resources →
              </div>
            </a>

            {/* Policy Makers & Advocates - Non-Technical */}
            <a
              href={`${docsBaseUrl}/for-advocates`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <AcademicCapIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                Policy Makers
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
              href={`${docsBaseUrl}/for-developers`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <CodeBracketIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                Developers
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
              href={`${docsBaseUrl}/intro`}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all group"
            >
              <CommandLineIcon className="h-12 w-12 mb-4 group-hover:scale-110 transition-transform" style={{ color: '#354F52' }} />
              <h3 className="text-2xl font-bold mb-3" style={{ color: '#354F52' }}>
                Full Docs
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

      {/* Contact Us CTA */}
      <section id="contact" className="py-20 px-4 bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <EnvelopeIcon className="h-16 w-16 mx-auto mb-6" style={{ color: '#354F52' }} />
            <h2 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: '#354F52' }}>
              Get in Touch
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Questions, feedback, or ideas? We'd love to hear from you.
              Report bugs, request features, or ask questions about jurisdiction coverage.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/getcommunityone/open-navigator-for-engagement/issues/new"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-8 py-4 rounded-lg text-white font-semibold transition-all hover:shadow-lg"
                style={{ backgroundColor: '#354F52' }}
              >
                <EnvelopeIcon className="h-5 w-5 mr-2" />
                Contact Us on GitHub
              </a>
              <a
                href="mailto:john.bowyer@communityone.com"
                className="inline-flex items-center justify-center px-8 py-4 rounded-lg bg-white border-2 text-[#354F52] font-semibold transition-all hover:bg-gray-50"
                style={{ borderColor: '#354F52' }}
              >
                Email Us Directly
              </a>
            </div>
            <p className="text-sm text-gray-500 mt-6">
              Your feedback helps us improve the platform for everyone.
            </p>
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
            Making community impact accessible to everyone
          </p>
          <div className="flex justify-center gap-8 text-sm text-gray-400">
            <a href={`${docsBaseUrl}/intro`} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Documentation</a>
            <a href={`${apiBaseUrl}/api/docs`} target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">API</a>
            <Link to="/explore" className="hover:text-white transition-colors">Explore</Link>
            <a href="https://github.com/getcommunityone/open-navigator-for-engagement" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">GitHub</a>
          </div>
          <p className="text-gray-500 text-sm mt-6">
            © 2026 CommunityOne. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
