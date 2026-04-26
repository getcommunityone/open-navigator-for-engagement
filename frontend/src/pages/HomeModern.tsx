import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
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
  HeartIcon
} from '@heroicons/react/24/outline'
import { useLocation as useLocationContext } from '../contexts/LocationContext'
import AddressLookup from '../components/AddressLookup'

export default function HomeModern() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')
  const [activeSection, setActiveSection] = useState('hero')
  const { setLocation } = useLocationContext()

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
    if (keyword.trim()) {
      navigate(`/documents?search=${encodeURIComponent(keyword)}`)
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
    { id: 'get-started', label: 'Get Started' },
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

          {/* Search Box */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-6 w-6 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search topics: housing, health, education..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#354F52] focus:border-transparent text-gray-900"
                />
              </div>
              <button
                type="submit"
                className="px-8 py-4 rounded-xl text-white font-semibold hover:shadow-lg transition-all"
                style={{ backgroundColor: '#354F52' }}
              >
                Search
              </button>
            </div>
          </form>

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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { value: '90,000+', label: 'Cities & Counties', color: '#354F52' },
              { value: '3M+', label: 'Nonprofits Tracked', color: '#52796F' },
              { value: '15,000+', label: 'Decisions Analyzed', color: '#84A98C' },
              { value: '100%', label: 'Free & Open', color: '#4A90E2' },
            ].map((stat, index) => (
              <div key={index} className="text-center p-8 rounded-2xl bg-gradient-to-br from-gray-50 to-white">
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

      {/* Get Started Section */}
      <section id="get-started" className="py-20 px-4" style={{ background: 'linear-gradient(135deg, #354F52 0%, #52796F 100%)' }}>
        <div className="max-w-4xl mx-auto text-center">
          <RocketLaunchIcon className="h-16 w-16 mx-auto mb-6 text-white" />
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of engaged citizens tracking local decisions
          </p>

          {/* Address Lookup */}
          <div className="bg-white rounded-2xl p-8 shadow-2xl">
            <h3 className="text-2xl font-bold mb-4" style={{ color: '#354F52' }}>
              Find Your Local Community
            </h3>
            <p className="text-gray-600 mb-6">
              Enter your address to discover local leaders, meetings, and charities
            </p>
            <AddressLookup onLocationFound={handleAddressFound} />
          </div>

          {/* Alternative CTAs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <Link
              to="/people"
              className="px-8 py-4 bg-white rounded-xl font-semibold hover:shadow-xl transition-all"
              style={{ color: '#354F52' }}
            >
              Browse Leaders →
            </Link>
            <Link
              to="/nonprofits"
              className="px-8 py-4 bg-white/10 border-2 border-white rounded-xl text-white font-semibold hover:bg-white/20 transition-all"
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
