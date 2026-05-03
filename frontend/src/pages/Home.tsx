import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState, Fragment, useEffect } from 'react'
import { Tab } from '@headlessui/react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
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
  MapPinIcon,
  PlusIcon,
  BellIcon,
  FireIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  ChevronDownIcon,
  MapIcon,
  BellAlertIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'
import AddressLookup from '../components/AddressLookup'
import { useLocation as useLocationContext } from '../contexts/LocationContext'

// Trending topic/cause interface
interface TrendingCause {
  name: string
  icon: string
  category: string
  description?: string
  image_url?: string
  popularity_rank?: number
}

// Featured stories for tabbed hero banner
const FEATURED_STORIES = [
  {
    type: 'hero',
    title: 'CommunityOne',
    subtitle: 'Track Local Decisions. Take Action.',
    description: 'Follow leaders, charities, and causes in your community.',
    stats: '925 jurisdictions • 43.7K nonprofits • 362 leaders • 650+ causes • 100% free',
    category: 'Home',
    link: '/'
  },
  {
    type: 'story',
    title: 'World Press Freedom Day: 43,726 Nonprofits Fighting for Transparency',
    subtitle: 'How local journalism and civic organizations are tracking government decisions across 925 jurisdictions',
    image: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&h=600&fit=crop',
    category: 'Civic Engagement',
    link: '/search?q=press+freedom'
  },
  {
    type: 'story',
    title: 'AI Policy Tracking: 15,000+ Government Decisions Analyzed',
    subtitle: 'Machine learning models identify patterns in legislative discussions and regulatory frameworks',
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=600&fit=crop',
    category: 'Artificial Intelligence',
    link: '/search?q=artificial+intelligence'
  },
  {
    type: 'story',
    title: 'Healthcare Access: Dental Clinics in Focus',
    subtitle: 'Tracking 8,500+ dental health providers and community health initiatives nationwide',
    image: 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&h=600&fit=crop',
    category: 'Health & Medicine',
    link: '/search?q=dental+health'
  },
  {
    type: 'story',
    title: 'Local Sports Funding: $2.5B in Community Programs',
    subtitle: 'Analysis of recreation budget allocation across 12,000+ jurisdictions',
    image: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&h=600&fit=crop',
    category: 'Sports & Recreation',
    link: '/search?q=sports+funding'
  },
  {
    type: 'story',
    title: 'Social Media Policies: Cities Set New Guidelines',
    subtitle: 'How local governments are establishing digital communication standards',
    image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=1200&h=600&fit=crop',
    category: 'Technology',
    link: '/search?q=social+media+policy'
  },
  {
    type: 'story',
    title: 'Business Development: 8,000+ Economic Initiatives',
    subtitle: 'Economic development zones, tax incentives, and small business support programs',
    image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=600&fit=crop',
    category: 'Business & Markets',
    link: '/search?q=business+development'
  },
  {
    type: 'story',
    title: 'Government Transparency: 12,000+ Hours of Meeting Video',
    subtitle: 'Comprehensive archive of city council, county board, and planning commission meetings',
    image: 'https://images.unsplash.com/photo-1555421689-d68471e189f2?w=1200&h=600&fit=crop',
    category: 'Government',
    link: '/documents'
  },
]

export default function Home() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [keyword, setKeyword] = useState('')
  const [searchScope, setSearchScope] = useState('city') // city, county, state, community (school)
  const [selectedTab, setSelectedTab] = useState(0)
  const [selectedStoryTab, setSelectedStoryTab] = useState(0)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showLoginMenu, setShowLoginMenu] = useState(false)
  const { location, setLocation } = useLocationContext()
  const { user, isAuthenticated, login, isLoading } = useAuth()

  const DOCS_URL = import.meta.env.PROD ? 'https://www.communityone.com/docs/intro' : 'http://localhost:3000/docs/intro'

  // Fetch trending causes from database (replaces hardcoded TRENDING_TOPICS)
  const { data: trendingData } = useQuery({
    queryKey: ['trending-causes'],
    queryFn: async () => {
      const response = await api.get('/trending', {
        params: {
          source: 'mixed',  // Mix of everyorg and ntee causes
          limit: 12
        }
      })
      return response.data
    },
    staleTime: 5 * 60 * 1000,  // Cache for 5 minutes
  })

  // Use database causes if available, fallback to empty array while loading
  const trendingTopics = trendingData?.causes || []

  // Live search preview (type-ahead with actual results from API)
  const { data: previewResults, isLoading: previewLoading, error: previewError } = useQuery({
    queryKey: ['search-preview-home', keyword, location?.state],
    queryFn: async () => {
      console.log('🔍 [Home] Fetching preview for:', keyword, 'in state:', location?.state);
      if (!keyword || keyword.length < 2) {
        console.log('⚠️ [Home] Query too short, skipping');
        return null;
      }
      
      try {
        const url = '/search/';
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
        const response = await api.get(url, { params });
        console.log('📥 [Home] API Response:', response.data);
        console.log('📊 [Home] Total results:', response.data.total_results);
        return response.data;
      } catch (error: any) {
        console.error('❌ [Home] Search preview error:', error);
        console.error('❌ [Home] Error details:', {
          message: error.message,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data
        });
        throw error;
      }
    },
    enabled: keyword.length >= 2 && showSuggestions,
    staleTime: 1000,
    retry: 1, // Only retry once on error
    retryDelay: 1000
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
    console.log('🔍 [Home] Search submitted:', { keyword, location: location?.state, searchScope });
    
    if (keyword.trim()) {
      const params = new URLSearchParams()
      params.set('q', keyword.trim())
      
      // Add location context if available
      if (location && location.state) {
        params.set('state', location.state)
        console.log('📍 [Home] Adding state filter:', location.state);
      }
      
      const searchUrl = `/search?${params.toString()}`;
      console.log('🚀 [Home] Navigating to:', searchUrl);
      navigate(searchUrl)
    } else {
      console.warn('⚠️ [Home] Search submitted with empty keyword');
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

  // Smooth scroll to section with offset for sticky header
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      const offset = 80 // Account for sticky header (h-20 = 80px)
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - offset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <a 
              href="#" 
              onClick={(e) => {
                e.preventDefault()
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <img 
                src="/communityone_logo.svg" 
                alt="CommunityOne Logo" 
                className="h-12"
              />
              <div className="flex flex-col">
                <span className="text-xl font-bold" style={{ color: '#354F52' }}>
                  Open Navigator
                </span>
                <span className="text-xs text-gray-500 -mt-1 group-hover:text-[#354F52] transition-colors">
                  The open path to everything local
                </span>
              </div>
            </a>

            {/* Desktop Navigation Links - Centered with underline */}
            <div className="hidden md:flex items-center gap-8">
              <button 
                onClick={() => scrollToSection('features')} 
                className="text-sm font-medium text-gray-600 hover:text-[#354F52] transition-colors pb-1 border-b-2 border-transparent hover:border-[#354F52] cursor-pointer"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('how-it-works')} 
                className="text-sm font-medium text-gray-600 hover:text-[#354F52] transition-colors pb-1 border-b-2 border-transparent hover:border-[#354F52] cursor-pointer"
              >
                How It Works
              </button>
              <button 
                onClick={() => scrollToSection('impact')} 
                className="text-sm font-medium text-gray-600 hover:text-[#354F52] transition-colors pb-1 border-b-2 border-transparent hover:border-[#354F52] cursor-pointer"
              >
                Impact
              </button>
              <a 
                href={DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-gray-600 hover:text-[#354F52] transition-colors pb-1 border-b-2 border-transparent hover:border-[#354F52]"
              >
                Documentation
              </a>
              <a 
                href="mailto:johnbowyer@communityone.com" 
                className="text-sm font-medium text-gray-600 hover:text-[#354F52] transition-colors pb-1 border-b-2 border-transparent hover:border-[#354F52]"
              >
                Contact
              </a>
            </div>

            {/* Desktop CTA Button */}
            <div className="hidden md:flex items-center gap-3">
              {isLoading ? (
                <div className="px-3 py-2">
                  <div className="animate-spin h-8 w-8 border-3 border-gray-300 border-t-primary-600 rounded-full"></div>
                </div>
              ) : isAuthenticated && user ? (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100">
                  {user.avatar_url ? (
                    <img 
                      src={user.avatar_url} 
                      alt={user.full_name || user.email}
                      className="h-8 w-8 rounded-full border-2 border-primary-500 object-cover"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-bold text-sm">
                      {(user.full_name || user.username || user.email).charAt(0).toUpperCase()}
                    </div>
                  )}
                  <span className="text-sm font-medium text-gray-700">
                    {user.full_name || user.username || user.email.split('@')[0]}
                  </span>
                </div>
              ) : (
                <div className="relative">
                  <button
                    onClick={() => setShowLoginMenu(!showLoginMenu)}
                    className="h-[42px] px-6 text-white rounded-lg transition-colors text-sm font-semibold flex items-center gap-2"
                    style={{ backgroundColor: '#354F52' }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2e4346'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#354F52'}
                  >
                    <UserCircleIcon className="h-5 w-5" />
                    <span>Register/Login</span>
                    <ChevronDownIcon className="h-4 w-4" />
                  </button>
                  
                  {showLoginMenu && (
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                      <div className="px-4 py-2 border-b border-gray-200">
                        <p className="text-sm font-medium text-gray-900">Sign in with:</p>
                      </div>
                      <button
                        onClick={() => { login('google'); setShowLoginMenu(false); }}
                        className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-100 transition-colors"
                      >
                        <div className="w-6 h-6 flex items-center justify-center flex-shrink-0">
                          <svg viewBox="0 0 24 24" className="w-5 h-5" preserveAspectRatio="xMidYMid meet">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                          </svg>
                        </div>
                        <span className="text-sm font-medium text-gray-700">Google</span>
                      </button>
                      <button
                        onClick={() => { login('facebook'); setShowLoginMenu(false); }}
                        className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-100 transition-colors"
                      >
                        <div className="w-6 h-6 flex items-center justify-center">
                          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="#1877F2">
                            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                          </svg>
                        </div>
                        <span className="text-sm font-medium text-gray-700">Facebook</span>
                      </button>
                      <button
                        onClick={() => { login('github'); setShowLoginMenu(false); }}
                        className="flex items-center gap-3 w-full px-4 py-3 hover:bg-gray-100 transition-colors"
                      >
                        <div className="w-6 h-6 flex items-center justify-center">
                          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="#181717">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                        </div>
                        <span className="text-sm font-medium text-gray-700">GitHub</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
              <Link
                to="/explore"
                className="h-[42px] px-6 rounded-lg text-white font-semibold hover:shadow-lg transition-all flex items-center"
                style={{ backgroundColor: '#354F52' }}
              >
                Explore Now
              </Link>
            </div>

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
              <button
                className="block w-full text-left px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100"
                onClick={() => {
                  scrollToSection('features')
                  setMobileMenuOpen(false)
                }}
              >
                Features
              </button>
              <button
                className="block w-full text-left px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100"
                onClick={() => {
                  scrollToSection('how-it-works')
                  setMobileMenuOpen(false)
                }}
              >
                How It Works
              </button>
              <button
                className="block w-full text-left px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100"
                onClick={() => {
                  scrollToSection('impact')
                  setMobileMenuOpen(false)
                }}
              >
                Impact
              </button>
              <a
                href={DOCS_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="block px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100"
                onClick={() => setMobileMenuOpen(false)}
              >
                Documentation
              </a>
              <a
                href="mailto:johnbowyer@communityone.com"
                className="block px-4 py-3 rounded-lg text-base font-medium text-gray-700 hover:bg-gray-100"
                onClick={() => setMobileMenuOpen(false)}
              >
                Contact
              </a>
            </div>
          </div>
        )}
      </nav>

      {/* Trending Topics Bar - Compact and Professional */}
      <div className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="flex items-center gap-3">
            {/* Trending Icon */}
            <FireIcon className="h-5 w-5 text-orange-500 flex-shrink-0" />
            
            {/* Scrollable topics row */}
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide flex-1">
              {trendingTopics.slice(0, 12).map((topic: TrendingCause) => (
                <button
                  key={topic.name}
                  onClick={() => navigate(`/search?q=${encodeURIComponent(topic.name)}`)}
                  className="group inline-flex items-center gap-1.5 px-2.5 py-1 bg-gray-50 border border-gray-200 rounded-md hover:border-[#354F52] hover:bg-[#354F52]/5 transition-all text-xs whitespace-nowrap flex-shrink-0"
                >
                  <span className="font-medium text-gray-700 group-hover:text-[#354F52]">{topic.name}</span>
                  <PlusIcon className="h-3 w-3 text-gray-400 group-hover:text-[#354F52]" />
                </button>
              ))}
              <button
                onClick={() => navigate('/search')}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[#354F52] text-white rounded-md hover:bg-[#2e4346] transition-all text-xs whitespace-nowrap flex-shrink-0"
              >
                <BellIcon className="h-3 w-3" />
                <span className="font-medium">View All</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Story Hero with gradient background */}
      <div className="py-8" style={{ background: 'linear-gradient(135deg, #F1F5F9 0%, #E8EEF2 100%)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-6">
            {/* Left Sidebar Navigation */}
            <div className="hidden lg:block w-64 flex-shrink-0">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 sticky top-24 h-[500px] flex flex-col">
                <h3 className="text-lg font-bold mb-4" style={{ color: '#354F52' }}>
                  Quick Navigation
                </h3>
                <nav className="space-y-2 flex-1">
                  <Link
                    to="/explore"
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-[#354F52] hover:text-white transition-all group"
                  >
                    <MapIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span className="font-medium">Explore</span>
                  </Link>
                  <Link
                    to="/search"
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-[#354F52] hover:text-white transition-all group"
                  >
                    <MagnifyingGlassIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span className="font-medium">Search</span>
                  </Link>
                  <Link
                    to="/policy-map"
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-[#354F52] hover:text-white transition-all group"
                  >
                    <ChartBarIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span className="font-medium">Policy Map</span>
                  </Link>
                  <Link
                    to="/nonprofits"
                    className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-[#354F52] hover:text-white transition-all group"
                  >
                    <BuildingLibraryIcon className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    <span className="font-medium">Nonprofits</span>
                  </Link>
                </nav>
                
                {/* Additional Info */}
                <div className="mt-auto pt-6 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <BellAlertIcon className="h-4 w-4 text-primary-600" />
                    <span className="font-semibold">Stay Updated</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-3">
                    Get alerts for new policies and opportunities in your area
                  </p>
                  <Link
                    to="/explore"
                    className="block w-full px-4 py-2 text-center bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                  >
                    Get Started
                  </Link>
                </div>
              </div>
            </div>

            {/* Hero Carousel with Search as First Item */}
            <div className="flex-1">
              <div className="animate-[slideUp_0.6s_ease-out]">
                {/* Story Content - Conditional rendering based on type */}
                {FEATURED_STORIES[selectedStoryTab].type === 'hero' ? (
                  /* Hero Search Interface */
                  <div className="relative overflow-hidden rounded-2xl shadow-2xl h-[500px] flex items-center justify-center p-8 md:p-12 bg-gradient-to-br from-gray-50 to-white">
                    <div className="text-center max-w-4xl w-full">
                      <p className="text-xl md:text-2xl text-gray-600 mb-4">
                        {FEATURED_STORIES[selectedStoryTab].title}
                      </p>
                      <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight" style={{
                        background: 'linear-gradient(135deg, #354F52 0%, #52796F 50%, #84A98C 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                      }}>
                        {FEATURED_STORIES[selectedStoryTab].subtitle}
                      </h1>
                      <p className="text-lg md:text-xl text-gray-600 mb-6">
                        {FEATURED_STORIES[selectedStoryTab].description}
                      </p>
                      <p className="text-sm md:text-base text-gray-500 mb-8 font-medium">
                        {FEATURED_STORIES[selectedStoryTab].stats}
                      </p>
                      
                      {/* Search Box */}
                      <div className="max-w-3xl mx-auto mb-6">
                        <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 p-4">
                          <form onSubmit={handleSearch}>
                            {/* Search Input and Scope Dropdown on Same Line */}
                            <div className="flex gap-2 mb-3 relative">
                              <div className="flex-1 relative">
                                <input
                                  type="text"
                                  placeholder="Search for topics, people, organizations, or causes..."
                                  value={keyword}
                                  onChange={handleKeywordChange}
                                  onFocus={() => {
                                    if (keyword.length >= 2) {
                                      setShowSuggestions(true)
                                    }
                                  }}
                                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                                  className="w-full px-4 py-2 text-base border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent text-gray-900"
                                />
                                
                                {/* Error Display - Below Input */}
                                {keyword.length >= 2 && previewError && (
                                  <div className="absolute top-full left-0 right-0 mt-2 z-20 bg-red-50 border border-red-200 rounded-lg shadow-lg p-3">
                                    <div className="flex items-start gap-2">
                                      <svg className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                      </svg>
                                      <div>
                                        <p className="text-sm font-medium text-red-800">Search Error</p>
                                        <p className="text-xs text-red-600 mt-1">
                                          {(previewError as any)?.response?.status === 404 
                                            ? 'API endpoint not found. Server may still be starting.'
                                            : 'Unable to fetch results. Please try again.'}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                )}
                                
                                {/* Loading Display - Below Input */}
                                {keyword.length >= 2 && previewLoading && (
                                  <div className="absolute top-full left-0 right-0 mt-2 z-20 bg-white border border-gray-200 rounded-lg shadow-lg p-3">
                                    <div className="flex items-center gap-2">
                                      <svg className="animate-spin h-4 w-4 text-[#354F52]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                      </svg>
                                      <span className="text-sm text-gray-600">Searching...</span>
                                    </div>
                                  </div>
                                )}
                              </div>
                              
                              {/* Search Scope Dropdown */}
                              {location ? (
                                <select
                                  value={searchScope}
                                  onChange={(e) => setSearchScope(e.target.value)}
                                  className="px-4 py-2 text-sm border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent bg-white text-gray-900 whitespace-nowrap"
                                >
                                  <option value="city">My City ({location.city})</option>
                                  <option value="county">My County ({location.county || 'County'})</option>
                                  <option value="state">My State ({location.state})</option>
                                  <option value="community">School Board ({location.city})</option>
                                </select>
                              ) : null}
                            </div>
                            
                            <div className="flex gap-2 items-center">
                              <button
                                onClick={() => setSelectedTab(1)}
                                type="button"
                                className="px-3 py-2 text-sm font-medium text-[#354F52] hover:text-[#52796F] transition-colors whitespace-nowrap"
                              >
                                📍 Find My Community
                              </button>
                              
                              <button
                                type="submit"
                                className="flex-1 px-6 py-2 bg-[#354F52] text-white rounded-lg hover:bg-[#2e4346] transition-colors font-semibold shadow-lg text-sm"
                              >
                                Search
                              </button>
                            </div>
                          </form>
                        </div>
                      </div>
                    </div>

                    {/* Navigation Arrows */}
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        setSelectedStoryTab((prev) => (prev === 0 ? FEATURED_STORIES.length - 1 : prev - 1))
                      }}
                      className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center text-gray-700 transition-all"
                      aria-label="Previous story"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        setSelectedStoryTab((prev) => (prev === FEATURED_STORIES.length - 1 ? 0 : prev + 1))
                      }}
                      className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center text-gray-700 transition-all"
                      aria-label="Next story"
                    >
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>

                    {/* Story Indicators */}
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                      {FEATURED_STORIES.map((_, idx) => (
                        <button
                          key={idx}
                          onClick={(e) => {
                            e.preventDefault()
                            setSelectedStoryTab(idx)
                          }}
                          className={`w-2 h-2 rounded-full transition-all ${
                            selectedStoryTab === idx
                              ? 'bg-gray-700 w-8'
                              : 'bg-gray-400 hover:bg-gray-600'
                          }`}
                          aria-label={`Go to story ${idx + 1}`}
                        />
                      ))}
                    </div>
                  </div>
                ) : (
                  /* Regular Story with Image */
                  <Link to={FEATURED_STORIES[selectedStoryTab].link} className="group block">
                    <div className="relative overflow-hidden rounded-2xl bg-gray-900 shadow-2xl h-[500px]">
                      <img
                        src={FEATURED_STORIES[selectedStoryTab].image}
                        alt={FEATURED_STORIES[selectedStoryTab].title}
                        className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-50 transition-opacity duration-300"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
                      <div className="absolute bottom-0 left-0 right-0 p-8 md:p-12">
                        <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 leading-tight group-hover:text-primary-300 transition-colors">
                          {FEATURED_STORIES[selectedStoryTab].title}
                        </h2>
                        <p className="text-lg md:text-xl text-gray-200 max-w-3xl">
                          {FEATURED_STORIES[selectedStoryTab].subtitle}
                        </p>
                      </div>

                      {/* Story Navigation Arrows */}
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          setSelectedStoryTab((prev) => (prev === 0 ? FEATURED_STORIES.length - 1 : prev - 1))
                        }}
                        className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-all"
                        aria-label="Previous story"
                      >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          setSelectedStoryTab((prev) => (prev === FEATURED_STORIES.length - 1 ? 0 : prev + 1))
                        }}
                        className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-all"
                        aria-label="Next story"
                      >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>

                      {/* Story Indicators */}
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                        {FEATURED_STORIES.map((_, idx) => (
                          <button
                            key={idx}
                            onClick={(e) => {
                              e.preventDefault()
                              setSelectedStoryTab(idx)
                            }}
                            className={`w-2 h-2 rounded-full transition-all ${
                              selectedStoryTab === idx
                                ? 'bg-white w-8'
                                : 'bg-white/50 hover:bg-white/75'
                            }`}
                            aria-label={`Go to story ${idx + 1}`}
                          />
                        ))}
                      </div>
                    </div>
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Find My Community Modal */}
      {selectedTab === 1 && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedTab(0)}>
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: '#354F52' }}>
                Find My Community
              </h2>
              <button
                onClick={() => setSelectedTab(0)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label="Close"
              >
                <XMarkIcon className="h-6 w-6 text-gray-500" />
              </button>
            </div>
            <p className="text-gray-600 mb-6">
              Enter your address to find local organizations, city councils, county boards, school districts, and charities near you
            </p>
            <AddressLookup onLocationFound={handleAddressFound} />
            
            {/* Success message */}
            {location && (
              <div className="mt-8 p-6 bg-green-50 border-2 border-green-200 rounded-xl">
                <div className="flex items-start gap-3 mb-4">
                  <CheckCircleIcon className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-green-900 mb-1">
                      Location Set Successfully!
                    </h3>
                    <p className="text-green-700">
                      You're all set for <strong>{location.city}, {location.state}</strong>. You can now search for topics in your community.
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTab(0)}
                  className="w-full bg-green-600 hover:bg-green-700 text-white px-6 py-4 rounded-lg font-semibold text-lg flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl"
                >
                  <MagnifyingGlassIcon className="h-6 w-6" />
                  Start Searching
                  <ArrowRightIcon className="h-5 w-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Features Section */}
      <section id="features" className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12 animate-[slideUp_0.8s_ease-out_0.8s_both]">
            <h2 className="text-3xl md:text-4xl font-bold mb-2" style={{ color: '#354F52' }}>
              Everything You Need
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-[#52796F] to-[#84A98C] mx-auto rounded mb-4"></div>
            <p className="text-lg text-gray-600">
              Powerful tools to stay informed and engaged
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-[slideUp_0.8s_ease-out_1s_both]">
            <Link
              to="/documents"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#354F52] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#354F5215' }}
              >
                <DocumentTextIcon className="h-7 w-7" style={{ color: '#354F52' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Policy Decisions
              </h3>
              <p className="text-gray-600 mb-4">
                Track 500K+ meeting pages with decision analysis, deferral patterns, and stakeholder positions
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#354F52' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>

            <Link
              to="/analytics"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#52796F] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#52796F15' }}
              >
                <ChartBarIcon className="h-7 w-7" style={{ color: '#52796F' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Budget Analysis
              </h3>
              <p className="text-gray-600 mb-4">
                Compare budget rhetoric to reality with $2T+ in tracked spending and delta analysis
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#52796F' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>

            <Link
              to="/people"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#84A98C] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#84A98C15' }}
              >
                <UserGroupIcon className="h-7 w-7" style={{ color: '#84A98C' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Elected Officials
              </h3>
              <p className="text-gray-600 mb-4">
                Follow 362 officials across 925 jurisdictions with voting records and decision patterns
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#84A98C' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>

            <Link
              to="/policy-map"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#4A90E2] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#4A90E215' }}
              >
                <MapIcon className="h-7 w-7" style={{ color: '#4A90E2' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Policy Map
              </h3>
              <p className="text-gray-600 mb-4">
                Track state legislation and bills across all sessions. Search 13,000+ bills by topic and status
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#4A90E2' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>

            <Link
              to="/nonprofits"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#9B59B6] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#9B59B615' }}
              >
                <BuildingLibraryIcon className="h-7 w-7" style={{ color: '#9B59B6' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Nonprofits & Churches
              </h3>
              <p className="text-gray-600 mb-4">
                43,726 nonprofits including 4,372 churches with financial data from 5 states
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#9B59B6' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>

            <Link
              to="/debate-grader"
              className="group bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 hover:border-[#E74C3C] hover:shadow-xl transition-all"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
                style={{ backgroundColor: '#E74C3C15' }}
              >
                <BellAlertIcon className="h-7 w-7" style={{ color: '#E74C3C' }} />
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Fact-Checking
              </h3>
              <p className="text-gray-600 mb-4">
                Verify claims with integrated PolitiFact, FactCheck.org, and Google Fact Check data
              </p>
              <span className="inline-flex items-center gap-2 text-sm font-medium" style={{ color: '#E74C3C' }}>
                Learn more <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 px-4 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-2" style={{ color: '#354F52' }}>
              How It Works
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-[#52796F] to-[#84A98C] mx-auto rounded mb-4"></div>
            <p className="text-lg text-gray-600">
              Three simple steps to stay engaged with your community
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Step 1 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#354F52] text-white text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Discover
              </h3>
              <p className="text-gray-600">
                Search across 925 jurisdictions and 43,726 nonprofits to find topics, people, and causes that matter to you
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#52796F] text-white text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Track
              </h3>
              <p className="text-gray-600">
                Monitor legislation, meetings, and policy decisions with AI-powered analysis and real-time updates
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#84A98C] text-white text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-bold mb-3" style={{ color: '#354F52' }}>
                Engage
              </h3>
              <p className="text-gray-600">
                Take action by contacting officials, supporting causes, and participating in local democracy
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section id="impact" className="py-16 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-2" style={{ color: '#354F52' }}>
              Our Impact
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-[#52796F] to-[#84A98C] mx-auto rounded mb-4"></div>
            <p className="text-lg text-gray-600">
              Making civic engagement accessible to everyone
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {/* Stat 1 */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2" style={{ color: '#354F52' }}>
                925
              </div>
              <div className="text-gray-600 font-medium">
                Jurisdictions Tracked
              </div>
            </div>

            {/* Stat 2 */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2" style={{ color: '#52796F' }}>
                43K+
              </div>
              <div className="text-gray-600 font-medium">
                Nonprofits Indexed
              </div>
            </div>

            {/* Stat 3 */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2" style={{ color: '#84A98C' }}>
                500K+
              </div>
              <div className="text-gray-600 font-medium">
                Meeting Pages
              </div>
            </div>

            {/* Stat 4 */}
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2" style={{ color: '#4A90E2' }}>
                13K+
              </div>
              <div className="text-gray-600 font-medium">
                Legislative Bills
              </div>
            </div>
          </div>

          {/* Mission Statement */}
          <div className="max-w-3xl mx-auto text-center bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8">
            <p className="text-lg text-gray-700 leading-relaxed mb-4">
              Open Navigator empowers communities by making local government transparent and accessible. 
              We believe informed citizens create stronger democracies.
            </p>
            <Link
              to="/explore"
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#354F52] text-white rounded-lg hover:bg-[#2e4346] transition-colors font-semibold"
            >
              Start Exploring <ArrowRightIcon className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Search Section (Collapsible) */}
      <div className="bg-gray-50 py-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 animate-[slideUp_0.8s_ease-out_0.8s_both]">
            <h2 className="text-3xl md:text-4xl font-bold mb-2" style={{ color: '#354F52' }}>
              Search Your Community
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-[#52796F] to-[#84A98C] mx-auto rounded mb-4"></div>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Track local governments and charities. Find leaders by name. Discover causes.{' '}
              <Link to="/jurisdictions" className="font-semibold text-[#52796F] hover:text-[#354F52] hover:underline hover:decoration-2 transition-colors">925 jurisdictions</Link>.{' '}
              <Link to="/search?types=organizations" className="font-semibold hover:underline">43,726 nonprofits</Link>. All free.
            </p>
          </div>

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
                            
                            {/* Error Display */}
                            {showSuggestions && previewError && (
                              <div className="absolute z-10 w-full mt-2 bg-red-50 border border-red-200 rounded-lg shadow-xl p-4">
                                <div className="flex items-start gap-3">
                                  <div className="flex-shrink-0">
                                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                  </div>
                                  <div className="flex-1">
                                    <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                                    <p className="mt-1 text-sm text-red-700">
                                      {(previewError as any)?.response?.status === 404 
                                        ? 'Search endpoint not found. The API may still be starting up.'
                                        : 'Unable to fetch search results. Please try again.'}
                                    </p>
                                    <p className="mt-2 text-xs text-red-600">
                                      Error details: {(previewError as any)?.message || 'Unknown error'}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Loading Display */}
                            {showSuggestions && previewLoading && (
                              <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl p-4">
                                <div className="flex items-center justify-center gap-3">
                                  <svg className="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                  </svg>
                                  <span className="text-sm text-gray-600">Searching...</span>
                                </div>
                              </div>
                            )}
                            
                            {/* Rich Preview Dropdown with Grouped Results */}
                            {showSuggestions && !previewLoading && !previewError && previewResults && previewResults.total_results > 0 && (
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
