import { Link } from 'react-router-dom';
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  MapIcon,
  ChartBarIcon,
  MicrophoneIcon,
  HeartIcon,
} from '@heroicons/react/24/outline';

interface ExploreCard {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
  color: string;
  stats?: string;
}

const exploreOptions: ExploreCard[] = [
  {
    title: 'Find Leaders',
    description: 'Discover elected officials, school board members, and community leaders in your area.',
    icon: UserGroupIcon,
    path: '/people',
    color: '#354F52',
    stats: '100K+ officials',
  },
  {
    title: 'Nonprofits',
    description: 'Explore over 3 million nonprofit organizations working on causes you care about.',
    icon: BuildingOfficeIcon,
    path: '/nonprofits',
    color: '#52796F',
    stats: '3M+ organizations',
  },
  {
    title: 'Opportunities',
    description: 'Find volunteer opportunities, community events, and ways to get involved locally.',
    icon: BriefcaseIcon,
    path: '/opportunities',
    color: '#84A98C',
    stats: 'Get involved',
  },
  {
    title: 'Meeting Minutes',
    description: 'Access and search through 500,000+ pages of public meeting minutes and records.',
    icon: DocumentTextIcon,
    path: '/documents',
    color: '#CAD2C5',
    stats: '500K+ pages',
  },
  {
    title: 'Jurisdiction Map',
    description: 'Explore 90,000+ cities, counties, and jurisdictions across the United States.',
    icon: MapIcon,
    path: '/heatmap',
    color: '#354F52',
    stats: '90K+ jurisdictions',
  },
  {
    title: 'Analytics Dashboard',
    description: 'View trends, insights, and data visualizations about civic engagement.',
    icon: ChartBarIcon,
    path: '/analytics',
    color: '#52796F',
    stats: 'Real-time data',
  },
  {
    title: 'Debate Analysis',
    description: 'Analyze political debates with AI-powered grading and sentiment analysis.',
    icon: MicrophoneIcon,
    path: '/debate-grader',
    color: '#84A98C',
    stats: 'AI-powered',
  },
  {
    title: 'My Profile',
    description: 'Follow leaders, organizations, and causes. Track your civic engagement journey.',
    icon: HeartIcon,
    path: '/profile',
    color: '#CAD2C5',
    stats: 'Personalized',
  },
];

export default function Explore() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">
              Explore Civic Engagement
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover leaders, organizations, and opportunities to make an impact in your community.
              Choose how you'd like to explore.
            </p>
          </div>
        </div>
      </div>

      {/* Exploration Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exploreOptions.map((option) => {
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
                    <Icon
                      className="h-7 w-7"
                      style={{ color: option.color }}
                    />
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

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-xl shadow-md p-8 max-w-2xl mx-auto border border-gray-100">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Not sure where to start?
            </h2>
            <p className="text-gray-600 mb-6">
              Start by finding your local leaders, or explore nonprofits working on causes you care about.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/people"
                className="px-6 py-3 rounded-lg text-white font-semibold hover:shadow-lg transition-all"
                style={{ backgroundColor: '#354F52' }}
              >
                Find My Leaders
              </Link>
              <Link
                to="/nonprofits"
                className="px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all border-2"
                style={{ borderColor: '#354F52', color: '#354F52' }}
              >
                Explore Nonprofits
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
