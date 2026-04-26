import { useState } from 'react'
import { MagnifyingGlassIcon, UserGroupIcon, AcademicCapIcon, UsersIcon, CodeBracketIcon } from '@heroicons/react/24/outline'

type PersonRole = 'decision-makers' | 'support' | 'public' | 'open-source'

interface Person {
  id: number
  name: string
  role: PersonRole
  specificRole: string
  organization: string
  location: string
  contact?: string
}

const roleCategories = {
  'decision-makers': {
    title: 'Decision Makers',
    subtitle: 'People who vote on policy and budgets',
    icon: UserGroupIcon,
    color: '#354F52',
    roles: [
      'Community Representatives',
      'The Decision Makers',
      'Board Members',
      'Policy Voters',
    ]
  },
  'support': {
    title: 'Support Staff',
    subtitle: 'People who help and advise',
    icon: AcademicCapIcon,
    color: '#64748B',
    roles: [
      'Expert Advisors',
      'Community Guides',
      'Program Staff',
    ]
  },
  'public': {
    title: 'Community Members',
    subtitle: 'Residents and advocates',
    icon: UsersIcon,
    color: '#8a9d9e',
    roles: [
      'Neighbors & Residents',
      'Parents & Families',
      'Advocates',
    ]
  },
  'open-source': {
    title: 'Open Source Contributors',
    subtitle: 'Civic tech maintainers and developers',
    icon: CodeBracketIcon,
    color: '#06B6D4',
    roles: [
      'Project Maintainers',
      'Core Contributors',
      'Community Developers',
    ]
  }
}

// Mock data - replace with API call
const mockPeople: Person[] = [
  {
    id: 1,
    name: 'Sarah Johnson',
    role: 'decision-makers',
    specificRole: 'Board Members',
    organization: 'City Council',
    location: 'District 3',
    contact: 'sjohnson@city.gov'
  },
  {
    id: 2,
    name: 'Michael Chen',
    role: 'decision-makers',
    specificRole: 'Policy Voters',
    organization: 'School Board',
    location: 'Zone 2',
    contact: 'mchen@schools.org'
  },
  {
    id: 3,
    name: 'Dr. Emily Martinez',
    role: 'support',
    specificRole: 'Expert Advisors',
    organization: 'Public Health Department',
    location: 'County Office',
    contact: 'emartinez@health.gov'
  },
  {
    id: 4,
    name: 'James Wilson',
    role: 'support',
    specificRole: 'Program Staff',
    organization: 'Community Health Center',
    location: 'Downtown Clinic',
    contact: 'jwilson@chc.org'
  },
  {
    id: 5,
    name: 'Maria Garcia',
    role: 'public',
    specificRole: 'Advocates',
    organization: 'Parents for Better Schools',
    location: 'Westside',
    contact: 'maria@pbs.org'
  },
  {
    id: 6,
    name: 'Alex Chen',
    role: 'open-source',
    specificRole: 'Project Maintainers',
    organization: 'openbudgetoakland',
    location: 'GitHub',
    contact: '@alexchen'
  },
  {
    id: 7,
    name: 'Jordan Taylor',
    role: 'open-source',
    specificRole: 'Core Contributors',
    organization: 'transitland',
    location: 'GitHub',
    contact: '@jordantaylor'
  },
  {
    id: 8,
    name: 'Sam Rodriguez',
    role: 'open-source',
    specificRole: 'Project Maintainers',
    organization: 'affordable-housing-finder',
    location: 'GitHub',
    contact: '@samrodriguez'
  },
  {
    id: 9,
    name: 'Casey Kim',
    role: 'open-source',
    specificRole: 'Community Developers',
    organization: 'health-equity-tracker',
    location: 'GitHub',
    contact: '@caseykim'
  },
]

export default function PeopleFinder() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRole, setSelectedRole] = useState<PersonRole | 'all'>('all')
  const [people] = useState<Person[]>(mockPeople)

  const filteredPeople = people.filter(person => {
    const matchesSearch = searchQuery === '' || 
      person.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      person.organization.toLowerCase().includes(searchQuery.toLowerCase()) ||
      person.location.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesRole = selectedRole === 'all' || person.role === selectedRole
    
    return matchesSearch && matchesRole
  })

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: '#354F52' }}>
          Find Leaders
        </h1>
        <p className="text-gray-600">
          Discover elected officials, decision makers, and community leaders in your area
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-8">
        <div className="relative">
          <input
            type="text"
            placeholder="Search by name, organization, repository, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <MagnifyingGlassIcon className="absolute left-4 top-3.5 h-6 w-6 text-gray-400" />
        </div>
      </div>

      {/* Role Filter Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <button
          onClick={() => setSelectedRole('all')}
          className={`p-4 rounded-lg border-2 transition-all ${
            selectedRole === 'all'
              ? 'border-[#354F52] bg-[#354F52] bg-opacity-10'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <div className="text-center">
            <div className="font-semibold" style={{ color: '#354F52' }}>All People</div>
            <div className="text-sm text-gray-500 mt-1">{people.length} total</div>
          </div>
        </button>

        {(Object.keys(roleCategories) as PersonRole[]).map((roleKey) => {
          const category = roleCategories[roleKey]
          const Icon = category.icon
          const count = people.filter(p => p.role === roleKey).length
          
          return (
            <button
              key={roleKey}
              onClick={() => setSelectedRole(roleKey)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedRole === roleKey
                  ? 'border-[#354F52] bg-[#354F52] bg-opacity-10'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex flex-col items-center text-center">
                <Icon className="h-8 w-8 mb-2" style={{ color: category.color }} />
                <div className="font-semibold" style={{ color: category.color }}>
                  {category.title}
                </div>
                <div className="text-sm text-gray-500 mt-1">{count} people</div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Role Categories Explanation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {(Object.keys(roleCategories) as PersonRole[]).map((roleKey) => {
          const category = roleCategories[roleKey]
          const Icon = category.icon
          
          return (
            <div key={roleKey} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center gap-3 mb-3">
                <Icon className="h-6 w-6" style={{ color: category.color }} />
                <h3 className="text-lg font-semibold" style={{ color: category.color }}>
                  {category.title}
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-3">{category.subtitle}</p>
              <ul className="space-y-1">
                {category.roles.map((role) => (
                  <li key={role} className="text-sm text-gray-700">
                    • {role}
                  </li>
                ))}
              </ul>
            </div>
          )
        })}
      </div>

      {/* Results */}
      <div>
        <h2 className="text-xl font-semibold mb-4" style={{ color: '#354F52' }}>
          {selectedRole === 'all' ? 'All People' : roleCategories[selectedRole].title}
          <span className="text-gray-500 font-normal ml-2">({filteredPeople.length} results)</span>
        </h2>

        {filteredPeople.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-500">No people found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPeople.map((person) => {
              const category = roleCategories[person.role]
              const Icon = category.icon
              
              return (
                <div key={person.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start gap-3 mb-3">
                    <Icon className="h-6 w-6 mt-1" style={{ color: category.color }} />
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg" style={{ color: '#354F52' }}>
                        {person.name}
                      </h3>
                      <p className="text-sm font-medium" style={{ color: category.color }}>
                        {person.specificRole}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">
                        {person.role === 'open-source' ? 'Repository:' : 'Organization:'}
                      </span>
                      {person.role === 'open-source' ? (
                        <a 
                          href={`https://github.com/${person.organization}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-cyan-600 hover:underline block"
                        >
                          {person.organization}
                        </a>
                      ) : (
                        <p className="text-gray-600">{person.organization}</p>
                      )}
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Location:</span>
                      <p className="text-gray-600">{person.location}</p>
                    </div>
                    {person.contact && (
                      <div>
                        <span className="font-medium text-gray-700">Contact:</span>
                        {person.role === 'open-source' && person.contact.startsWith('@') ? (
                          <a 
                            href={`https://github.com/${person.contact.substring(1)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-cyan-600 hover:underline block"
                          >
                            {person.contact}
                          </a>
                        ) : (
                          <p className="text-gray-600">{person.contact}</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
