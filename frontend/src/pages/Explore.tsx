import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  MapIcon,
  ChartBarIcon,
  MicrophoneIcon,
  BellAlertIcon,
  CalendarIcon,
  AcademicCapIcon,
  CheckBadgeIcon,
  PhoneIcon,
  ChatBubbleLeftRightIcon,
  HeartIcon,
  CodeBracketIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline';

interface ExploreCard {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  color: string;
  stats?: string;
}

// Policy Maker-focused sections
const policyMakerOptions: ExploreCard[] = [
  {
    title: 'Policy Decisions',
    description: 'Track decisions, budget deltas, stakeholder positions, and deferral patterns across government meetings.',
    icon: DocumentTextIcon,
    path: '/documents',
    color: '#354F52',
    stats: '500K+ meeting pages',
  },
  {
    title: 'Budget Analysis',
    description: 'Explore city, county, and school budgets with budget-to-minutes delta analysis showing rhetoric vs. reality.',
    icon: ChartBarIcon,
    path: '/analytics',
    color: '#52796F',
    stats: 'Real-time tracking',
  },
  {
    title: 'Elected Officials',
    description: 'Find local, state, and school board officials with voting records and decision patterns.',
    icon: UserGroupIcon,
    path: '/people',
    color: '#84A98C',
    stats: '100K+ officials',
  },
  {
    title: 'Demographics & Data',
    description: 'Access Census demographics, income, education, housing, and health insurance data by jurisdiction.',
    icon: MapIcon,
    path: '/heatmap',
    color: '#CAD2C5',
    stats: '90K+ jurisdictions',
  },
];

// Community & Advocate-focused sections
const advocateOptions: ExploreCard[] = [
  {
    title: 'Nonprofits & Churches',
    description: 'Search 43,726 nonprofits including 4,372 churches with financial data from 5 states.',
    icon: BuildingOfficeIcon,
    path: '/nonprofits',
    color: '#354F52',
    stats: '43,726 organizations',
  },
  {
    title: 'Advocacy Topics',
    description: 'Track what your community is discussing. Find advocacy alerts and engagement opportunities.',
    icon: BellAlertIcon,
    path: '/advocacy-topics',
    color: '#52796F',
    stats: 'Get involved',
  },
  {
    title: 'Grants & Funding',
    description: 'Discover government grants, foundation funding, and program delivery outcomes for nonprofits.',
    icon: BriefcaseIcon,
    path: '/analytics',
    color: '#84A98C',
    stats: 'Find funding',
  },
  {
    title: 'Fact-Checking',
    description: 'Verify claims from meetings and legislation with PolitiFact, FactCheck.org, and Google Fact Check data.',
    icon: MicrophoneIcon,
    path: '/fact-checking',
    color: '#CAD2C5',
    stats: 'Verified claims',
  },
];

// Developers-focused sections
const developerOptions: ExploreCard[] = [
  {
    title: 'Open Source Projects',
    description: 'Contribute to civic tech, data pipelines, AI models, and open government tools.',
    icon: CodeBracketIcon,
    path: '/opensource',
    color: '#354F52',
    stats: 'Join the community',
  },
  {
    title: 'Hackathons for Good',
    description: 'Build solutions for civic engagement, transparency, and community empowerment at our quarterly hackathons.',
    icon: RocketLaunchIcon,
    path: '/hackathons',
    color: '#52796F',
    stats: 'Make an impact',
  },
];

// Families & Individuals-focused sections
const familyOptions: ExploreCard[] = [
  {
    title: 'Community Events',
    description: 'Discover local government meetings, public hearings, town halls, and community events you can attend.',
    icon: CalendarIcon,
    path: '/events',
    color: '#354F52',
    stats: 'Attend & engage',
  },
  {
    title: 'Training & Services',
    description: 'Find community programs, educational workshops, health services, and family support resources.',
    icon: AcademicCapIcon,
    path: '/services',
    color: '#52796F',
    stats: 'Learn & grow',
  },
  {
    title: 'Voter Registration',
    description: 'Register to vote, find your polling place, check registration status, and learn about candidates.',
    icon: CheckBadgeIcon,
    path: '/analytics?topic=elections',
    color: '#84A98C',
    stats: 'Make your voice heard',
  },
  {
    title: 'Contact Your Representatives',
    description: 'Find contact information for elected officials, city council members, and school board representatives.',
    icon: PhoneIcon,
    path: '/people?view=contact',
    color: '#CAD2C5',
    stats: '100K+ officials',
  },
  {
    title: 'Submit Feedback',
    description: 'Provide public comments, share concerns, and participate in community decision-making processes.',
    icon: ChatBubbleLeftRightIcon,
    path: '/opportunities?type=feedback',
    color: '#52796F',
    stats: 'Be heard',
  },
  {
    title: 'Community Resources',
    description: 'Access food banks, housing assistance, healthcare, childcare, and other family support services.',
    icon: HeartIcon,
    path: '/nonprofits?category=family-services',
    color: '#84A98C',
    stats: 'Get help',
  },
];

export default function Explore() {
  // Scroll to top with smooth behavior when page loads
  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">
              Explore Open Navigator Data
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Access comprehensive data on government decisions, budgets, demographics, nonprofits, and community engagement.
            </p>
          </div>
        </div>
      </div>

      {/* Families & Individuals Section - FIRST */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">For Families & Individuals</h2>
          <p className="text-gray-600">Events, training, services, voter registration, and ways to engage with your community.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {familyOptions.map((option) => {
            const Icon = option.icon;
            return (
              <Link
                key={option.path}
                to={option.path}
                className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-gray-200"
              >
                <div className="p-6">
                  {/* Icon */}
                  <div
                    className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
                    style={{ backgroundColor: `${option.color}15` }}
                  >
                    <div style={{ color: option.color }}>
                      <Icon className="h-7 w-7" />
                    </div>
                  </div>

                  {/* Title and Stats */}
                  <div className="mb-3">
                    <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-[#354F52] transition-colors">
                      {option.title}
                    </h3>
                    {option.stats && (
                      <p className="text-sm font-medium" style={{ color: option.color }}>
                        {option.stats}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {option.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-4 flex items-center text-sm font-medium" style={{ color: option.color }}>
                    <span className="group-hover:translate-x-1 transition-transform duration-300">
                      Explore →
                    </span>
                  </div>
                </div>

                {/* Hover effect bar */}
                <div
                  className="h-1 w-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"
                  style={{ backgroundColor: option.color }}
                />
              </Link>
            );
          })}
        </div>

        {/* Policy Makers Section */}
        <div className="mb-8 mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">For Policy Makers & Government</h2>
          <p className="text-gray-600">Track decisions, budgets, officials, and demographic data across 90,000+ jurisdictions.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {policyMakerOptions.map((option) => {
            const Icon = option.icon;
            return (
              <Link
                key={option.path}
                to={option.path}
                className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-gray-200"
              >
                <div className="p-6">
                  {/* Icon */}
                  <div
                    className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
                    style={{ backgroundColor: `${option.color}15` }}
                  >
                    <div style={{ color: option.color }}>
                      <Icon className="h-7 w-7" />
                    </div>
                  </div>

                  {/* Title and Stats */}
                  <div className="mb-3">
                    <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-[#354F52] transition-colors">
                      {option.title}
                    </h3>
                    {option.stats && (
                      <p className="text-sm font-medium" style={{ color: option.color }}>
                        {option.stats}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {option.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-4 flex items-center text-sm font-medium" style={{ color: option.color }}>
                    <span className="group-hover:translate-x-1 transition-transform duration-300">
                      Explore →
                    </span>
                  </div>
                </div>

                {/* Hover effect bar */}
                <div
                  className="h-1 w-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"
                  style={{ backgroundColor: option.color }}
                />
              </Link>
            );
          })}
        </div>

        {/* Advocates Section */}
        <div className="mb-8 mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">For Advocates & Community Members</h2>
          <p className="text-gray-600">Find nonprofits, advocacy topics, funding, and fact-checked information.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {advocateOptions.map((option) => {
            const Icon = option.icon;
            return (
              <Link
                key={option.path}
                to={option.path}
                className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-gray-200"
              >
                <div className="p-6">
                  {/* Icon */}
                  <div
                    className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
                    style={{ backgroundColor: `${option.color}15` }}
                  >
                    <div style={{ color: option.color }}>
                      <Icon className="h-7 w-7" />
                    </div>
                  </div>

                  {/* Title and Stats */}
                  <div className="mb-3">
                    <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-[#354F52] transition-colors">
                      {option.title}
                    </h3>
                    {option.stats && (
                      <p className="text-sm font-medium" style={{ color: option.color }}>
                        {option.stats}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {option.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-4 flex items-center text-sm font-medium" style={{ color: option.color }}>
                    <span className="group-hover:translate-x-1 transition-transform duration-300">
                      Explore →
                    </span>
                  </div>
                </div>

                {/* Hover effect bar */}
                <div
                  className="h-1 w-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"
                  style={{ backgroundColor: option.color }}
                />
              </Link>
            );
          })}
        </div>

        {/* Developers Section */}
        <div className="mb-8 mt-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">For Developers & Civic Tech</h2>
          <p className="text-gray-600">Build with open data, contribute to open source, and join hackathons for social good.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {developerOptions.map((option) => {
            const Icon = option.icon;
            const isExternal = option.path.startsWith('http');
            
            const card = (
              <div className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-gray-200">
                <div className="p-6">
                  {/* Icon */}
                  <div
                    className="w-14 h-14 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
                    style={{ backgroundColor: `${option.color}15` }}
                  >
                    <div style={{ color: option.color }}>
                      <Icon className="h-7 w-7" />
                    </div>
                  </div>

                  {/* Title and Stats */}
                  <div className="mb-3">
                    <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-[#354F52] transition-colors">
                      {option.title}
                    </h3>
                    {option.stats && (
                      <p className="text-sm font-medium" style={{ color: option.color }}>
                        {option.stats}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {option.description}
                  </p>

                  {/* Arrow indicator */}
                  <div className="mt-4 flex items-center text-sm font-medium" style={{ color: option.color }}>
                    <span className="group-hover:translate-x-1 transition-transform duration-300">
                      {isExternal ? 'View on GitHub →' : 'Explore →'}
                    </span>
                  </div>
                </div>

                {/* Hover effect bar */}
                <div
                  className="h-1 w-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"
                  style={{ backgroundColor: option.color }}
                />
              </div>
            );
            
            return isExternal ? (
              <a
                key={option.path}
                href={option.path}
                target="_blank"
                rel="noopener noreferrer"
              >
                {card}
              </a>
            ) : (
              <Link key={option.path} to={option.path}>
                {card}
              </Link>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-xl shadow-md p-8 max-w-2xl mx-auto border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Access the Complete Dataset
            </h2>
            <p className="text-gray-600 mb-6">
              All data is available on HuggingFace with full documentation, APIs, and CSV/Parquet downloads.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://huggingface.co/datasets/CommunityOne/open-navigator-data"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 rounded-lg text-white font-semibold hover:shadow-lg transition-all"
                style={{ backgroundColor: '#354F52' }}
              >
                🤗 View on HuggingFace
              </a>
              <Link
                to="/docs/data-sources/data-model-erd"
                className="px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all border-2"
                style={{ borderColor: '#354F52', color: '#354F52' }}
              >
                📊 Explore Data Model
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Back to Home */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 text-center">
        <Link
          to="/"
          className="inline-flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
        >
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}
