import { useState, useEffect } from 'react'
import {
  RocketLaunchIcon,
  ChartBarIcon,
  BuildingLibraryIcon,
  GlobeAltIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  EnvelopeIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'

const datasets = [
  { name: 'Nonprofit Organizations', records: '1.95M', url: 'https://huggingface.co/datasets/CommunityOne/one-nonprofits-organizations', icon: BuildingLibraryIcon },
  { name: 'Nonprofit Financials', records: '1.95M', url: 'https://huggingface.co/datasets/CommunityOne/one-nonprofits-financials', icon: ChartBarIcon },
  { name: 'Nonprofit Programs', records: '1.95M', url: 'https://huggingface.co/datasets/CommunityOne/one-nonprofits-programs', icon: DocumentTextIcon },
  { name: 'Nonprofit Locations', records: '1.95M', url: 'https://huggingface.co/datasets/CommunityOne/one-nonprofits-locations', icon: GlobeAltIcon },
  { name: 'Public Meetings Calendar', records: '153K', url: 'https://huggingface.co/datasets/CommunityOne/one-meetings-calendar', icon: RocketLaunchIcon }
]

const features = [
  { title: '90,000+ Jurisdictions', description: 'Cities, counties, and state governments' },
  { title: '1.95M Nonprofits', description: 'Organizations with complete data' },
  { title: '153K+ Public Meetings', description: 'Agendas and transcripts' },
  { title: 'Open Source & Free', description: 'MIT License, accessible to all' }
]

function App() {
  const [activeSection, setActiveSection] = useState('home')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Smooth scroll to section
  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId)
    setMobileMenuOpen(false)
    
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
      const sections = ['home', 'datasets', 'about']
      const scrollPosition = window.scrollY + 150

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Navigation */}
      <nav className="bg-white/95 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <GlobeAltIcon className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">CommunityOne</h1>
                <p className="text-xs text-gray-600">The open path to everything local</p>
              </div>
            </div>

            {/* Desktop Navigation - Centered */}
            <div className="hidden md:flex items-center space-x-8 absolute left-1/2 transform -translate-x-1/2">
              <button
                onClick={() => scrollToSection('home')}
                className={`text-sm font-medium transition-all pb-1 ${
                  activeSection === 'home' 
                    ? 'text-primary-600 border-b-2 border-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection('datasets')}
                className={`text-sm font-medium transition-all pb-1 ${
                  activeSection === 'datasets' 
                    ? 'text-primary-600 border-b-2 border-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Datasets
              </button>
              <button
                onClick={() => scrollToSection('about')}
                className={`text-sm font-medium transition-all pb-1 ${
                  activeSection === 'about' 
                    ? 'text-primary-600 border-b-2 border-primary-600' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                About
              </button>
            </div>

            {/* Desktop CTA */}
            <a
              href="https://www.communityone.com"
              className="hidden md:inline-flex items-center px-6 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-all shadow-sm hover:shadow-md"
            >
              Launch App
              <ArrowRightIcon className="ml-2 h-4 w-4" />
            </a>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <div className="flex flex-col space-y-3">
                <button
                  onClick={() => scrollToSection('home')}
                  className={`text-left px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeSection === 'home' ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Home
                </button>
                <button
                  onClick={() => scrollToSection('datasets')}
                  className={`text-left px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeSection === 'datasets' ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  Datasets
                </button>
                <button
                  onClick={() => scrollToSection('about')}
                  className={`text-left px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeSection === 'about' ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  About
                </button>
                <a
                  href="https://www.communityone.com"
                  className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors text-center"
                >
                  Launch App
                </a>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <div id="home" className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-6 animate-[slideUp_0.6s_ease-out]">
              <CheckCircleIcon className="h-5 w-5 mr-2" />
              Open Source • 1.95M Nonprofits • MIT License
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 animate-[slideUp_0.8s_ease-out_0.2s_both]">
              Making Civic Data
              <span className="bg-gradient-to-r from-primary-600 to-green-600 bg-clip-text text-transparent"> Accessible</span>
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto animate-[slideUp_0.8s_ease-out_0.4s_both]">
              Comprehensive platform for discovering, analyzing, and tracking local government activities, 
              nonprofit organizations, and civic engagement opportunities across the United States.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-[slideUp_0.8s_ease-out_0.6s_both]">
              <a
                href="https://www.communityone.com"
                className="inline-flex items-center px-8 py-4 bg-primary-600 text-white text-lg font-medium rounded-xl hover:bg-primary-700 transition-all transform hover:scale-105 shadow-lg"
              >
                <RocketLaunchIcon className="h-6 w-6 mr-2" />
                Explore Platform
              </a>
              <button
                onClick={() => scrollToSection('datasets')}
                className="inline-flex items-center px-8 py-4 bg-white text-gray-700 text-lg font-medium rounded-xl hover:bg-gray-50 transition-all border-2 border-gray-200"
              >
                <ChartBarIcon className="h-6 w-6 mr-2" />
                Browse Datasets
              </button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-[slideUp_0.8s_ease-out_0.8s_both]">
            {features.map((feature, idx) => (
              <div key={idx} className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                <div className="text-3xl font-bold text-primary-600 mb-2">{feature.title}</div>
                <div className="text-gray-600">{feature.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Datasets Section */}
      <div id="datasets" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Open Datasets</h2>
          <p className="text-xl text-gray-600">High-quality, regularly-updated civic data for research and analysis</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {datasets.map((dataset, idx) => (
            <a
              key={idx}
              href={dataset.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-2xl hover:border-primary-300 transition-all transform hover:-translate-y-1"
            >
              <dataset.icon className="h-12 w-12 text-primary-600 mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{dataset.name}</h3>
              <div className="text-3xl font-bold text-primary-600 mb-3">{dataset.records}</div>
              <div className="text-sm text-gray-500 flex items-center">
                View dataset
                <ArrowRightIcon className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </a>
          ))}
        </div>
        <div className="mt-12 bg-gradient-to-r from-primary-50 to-green-50 rounded-xl p-8 text-center border border-primary-100">
          <h3 className="text-2xl font-bold text-gray-900 mb-3">1.95M Nonprofits, 13.8M Total Records</h3>
          <p className="text-gray-600 mb-6">All datasets are free to use under MIT License</p>
          <a
            href="https://huggingface.co/CommunityOne"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
          >
            View All on HuggingFace
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </a>
        </div>
      </div>

      {/* About Section */}
      <div id="about" className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">About CommunityOne</h2>
          <div className="prose prose-lg text-gray-600 space-y-6">
            <p>
              CommunityOne provides open-source tools and data for civic engagement, local government 
              transparency, and nonprofit discovery across the United States.
            </p>
            <h3 className="text-2xl font-bold text-gray-900 mt-8 mb-4">Mission</h3>
            <p>
              Making civic data accessible, usable, and actionable for:
            </p>
            <ul className="space-y-2">
              <li className="flex items-start">
                <CheckCircleIcon className="h-6 w-6 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                <span>Policy makers and advocates</span>
              </li>
              <li className="flex items-start">
                <CheckCircleIcon className="h-6 w-6 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                <span>Researchers and journalists</span>
              </li>
              <li className="flex items-start">
                <CheckCircleIcon className="h-6 w-6 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                <span>Nonprofit organizations</span>
              </li>
              <li className="flex items-start">
                <CheckCircleIcon className="h-6 w-6 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                <span>Engaged citizens</span>
              </li>
            </ul>
            <h3 className="text-2xl font-bold text-gray-900 mt-8 mb-4">Contact</h3>
            <div className="flex items-center space-x-3">
              <EnvelopeIcon className="h-6 w-6 text-primary-600" />
              <a href="mailto:john.bowyer@communityone.com" className="text-primary-600 hover:text-primary-700 font-medium">
                john.bowyer@communityone.com
              </a>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                Powered by open data from IRS, Census Bureau, local governments, and civic tech partners.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <GlobeAltIcon className="h-6 w-6" />
                <span className="font-bold">CommunityOne</span>
              </div>
              <p className="text-gray-400 text-sm">The open path to everything local</p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Links</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="https://www.communityone.com" className="hover:text-white transition-colors">Platform</a></li>
                <li><a href="https://www.communityone.com/docs" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="https://www.communityone.com/api/docs" className="hover:text-white transition-colors">API Docs</a></li>
                <li><a href="https://huggingface.co/CommunityOne" className="hover:text-white transition-colors">HuggingFace</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="https://github.com/getcommunityone" className="hover:text-white transition-colors flex items-center">
                  <CodeBracketIcon className="h-4 w-4 mr-2" />
                  GitHub
                </a></li>
                <li><a href="mailto:john.bowyer@communityone.com" className="hover:text-white transition-colors flex items-center">
                  <EnvelopeIcon className="h-4 w-4 mr-2" />
                  Contact
                </a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
            <p>© 2026 CommunityOne. Open source under MIT License.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
