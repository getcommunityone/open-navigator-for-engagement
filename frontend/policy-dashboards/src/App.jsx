import React, { useState } from 'react';
import HomePage from './components/HomePage';
import ImpactDashboard from './components/ImpactDashboard';
import TopicNavigation from './components/TopicNavigation';
import DecisionCard from './components/shared/DecisionCard';
import SplitScreenView from './components/SplitScreenView';
import { metadata } from './data/dashboardData';
import { Home, Grid } from 'lucide-react';

export default function App() {
  const [viewMode, setViewMode] = useState('browse'); // 'home', 'impact', 'browse', 'split-screen'
  const [sectorView, setSectorView] = useState('all'); // 'all', 'public', 'nonprofits', 'churches'
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [selectedPatterns, setSelectedPatterns] = useState([]);
  const [selectedResources, setSelectedResources] = useState([]);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const handlePersonaSelect = (persona, topic) => {
    setSelectedPersona(persona);
    setSelectedTopic(topic);
    setViewMode('impact');
  };
  
  const handleTopicSelect = (topicId) => {
    setSelectedTopics([topicId]);
    setViewMode('browse');
  };
  
  const handleTopicToggle = (topicId) => {
    setSelectedTopics(prev =>
      prev.includes(topicId)
        ? prev.filter(t => t !== topicId)
        : [...prev, topicId]
    );
  };
  
  const handlePatternToggle = (patternId) => {
    setSelectedPatterns(prev =>
      prev.includes(patternId)
        ? prev.filter(p => p !== patternId)
        : [...prev, patternId]
    );
  };
  
  const handleResourceToggle = (resourceId) => {
    setSelectedResources(prev =>
      prev.includes(resourceId)
        ? prev.filter(r => r !== resourceId)
        : [...prev, resourceId]
    );
  };
  
  const handleClearFilters = () => {
    setSelectedTopics([]);
    setSelectedPatterns([]);
    setSelectedResources([]);
    setStartDate(null);
    setEndDate(null);
    setSearchQuery('');
  };
  
  const handleBackToHome = () => {
    setViewMode('home');
    setSelectedPersona(null);
    setSelectedTopic(null);
    setSelectedDecision(null);
  };
  
  const handleDecisionClick = (decision) => {
    setSelectedDecision(decision);
    setViewMode('split-screen');
  };
  
  // Example decision data - would come from Python export
  const exampleDecisions = [
    {
      decision_summary: "Approval of $850,000 athletic turf replacement project",
      outcome: "Approved",
      primary_rationale: "Athletic facilities are essential for student engagement and community pride. The current turf is beyond its useful life and poses safety concerns.",
      supporters: [
        { name: "Board Member Johnson", role: "Board Member" },
        { name: "Athletic Director Smith", role: "Staff" }
      ],
      opponents: [
        { name: "Parent Coalition for Health", role: "Public" }
      ],
      vote_result: "6-1",
      meeting_date: "2026-03-15",
      tradeoffs_discussed: ["Athletic facilities vs. health screening programs"],
      evidence_cited: [{ source: "Athletic Department Report" }],
      policy_domain: "facilities",
      ntee_code: "N20" // Recreation, Sports, and Athletics
    },
    {
      decision_summary: "Tabled decision on dental screening partnership with West Alabama Dental Clinic",
      outcome: "Tabled for further study",
      primary_rationale: "Risk management concerns require additional legal review and liability analysis before proceeding with external health partnerships.",
      supporters: [
        { name: "Patricia Johnson, Risk Manager", role: "Staff" }
      ],
      opponents: [
        { name: "Dr. Sarah Martinez", role: "Public" },
        { name: "Parent Teacher Association", role: "Public" },
        { name: "Board Member Williams", role: "Board Member" }
      ],
      vote_result: "5-2 to table",
      meeting_date: "2026-01-18",
      tradeoffs_discussed: ["Preventive care vs. perceived liability risk"],
      evidence_cited: [{ source: "Risk Management Memo" }],
      policy_domain: "health",
      ntee_code: "E32", // School-Based Health Care
      community_gap: {
        description: "100% of surveyed parents want dental screenings for students",
        nonprofit_filling_gap: true
      }
    },
    {
      decision_summary: "Reduction of nursing staff from 5 FTE to 3 FTE",
      outcome: "Approved",
      primary_rationale: "Budget constraints necessitate cost reductions. Nursing positions will be restructured to focus on emergency response rather than preventive services.",
      supporters: [
        { name: "Superintendent Brown", role: "Staff" },
        { name: "Board Chair Thompson", role: "Board Member" }
      ],
      opponents: [
        { name: "School Nurses Association", role: "Public" },
        { name: "Board Member Lee", role: "Board Member" }
      ],
      vote_result: "4-3",
      meeting_date: "2026-02-20",
      tradeoffs_discussed: ["Cost savings vs. preventive health services"],
      evidence_cited: [{ source: "FY2026 Budget Proposal" }],
      policy_domain: "budget",
      ntee_code: "E40", // Health - General and Rehabilitative
      community_gap: {
        description: "Students lost access to preventive health services",
        nonprofit_filling_gap: true
      }
    }
  ];
  
  // Example nonprofit data - would come from IRS/GuideStar API
  const exampleNonprofits = [
    {
      name: "West Alabama Dental Initiative",
      ein: "63-1234567",
      ntee_code: "E32",
      ntee_description: "School-Based Health Care",
      mission: "Providing free dental screenings and preventive care to underserved students in West Alabama",
      services: [
        "Mobile dental unit visits to schools",
        "Free toothbrush and fluoride kits",
        "Dental education workshops for parents"
      ],
      annual_budget: 125000,
      students_served: 2400,
      contact: {
        website: "https://wadaldentalinitiative.org",
        email: "info@wadaldentalinitiative.org",
        phone: "(205) 555-0123"
      },
      volunteer_opportunities: true,
      accepting_board_members: true
    },
    {
      name: "Tuscaloosa Family Health Network",
      ein: "63-7654321",
      ntee_code: "E40",
      ntee_description: "Health - General and Rehabilitative",
      mission: "Connecting low-income families with preventive health services and wellness programs",
      services: [
        "Health screenings at community centers",
        "Nutrition education programs",
        "Mental health counseling referrals"
      ],
      annual_budget: 280000,
      families_served: 850,
      contact: {
        website: "https://tuscfamilyhealth.org",
        email: "contact@tuscfamilyhealth.org",
        phone: "(205) 555-0456"
      },
      volunteer_opportunities: true,
      accepting_board_members: false
    },
    {
      name: "After School Champions",
      ein: "63-9876543",
      ntee_code: "O50",
      ntee_description: "Youth Development Programs",
      mission: "Providing safe, enriching after-school programs that support academic success and healthy development",
      services: [
        "Homework help and tutoring",
        "Healthy snacks and meals",
        "Physical activity and sports",
        "Health and wellness workshops"
      ],
      annual_budget: 340000,
      youth_served: 450,
      contact: {
        website: "https://afterschoolchamps.org",
        email: "info@afterschoolchamps.org",
        phone: "(205) 555-0789"
      },
      volunteer_opportunities: true,
      accepting_board_members: true
    },
    {
      name: "First Baptist Church Tuscaloosa - Health Ministry",
      ein: "63-2345678",
      ntee_code: "X20",
      ntee_description: "Christian",
      mission: "Faith-based health outreach serving Tuscaloosa families through free dental kits, health screenings, and nutrition education",
      services: [
        "Free dental hygiene kits distribution",
        "Health screenings after Sunday service",
        "Nutrition education classes",
        "Mobile health unit partnership"
      ],
      annual_budget: 45000,
      families_served: 450,
      contact: {
        website: "https://fbctuscaloosa.org/health",
        email: "health@fbctuscaloosa.org",
        phone: "(205) 555-0200"
      },
      volunteer_opportunities: true,
      accepting_board_members: false
    },
    {
      name: "Tuscaloosa County Interfaith Dental Initiative",
      ein: "63-3456789",
      ntee_code: "X20",
      ntee_description: "Christian",
      mission: "Multi-faith collaboration providing free dental care to low-income students across Tuscaloosa County schools",
      services: [
        "Mobile dental unit serving Title I schools",
        "Free toothbrush and fluoride programs",
        "Parent education workshops",
        "Dental emergency fund for families"
      ],
      annual_budget: 180000,
      students_served: 1600,
      contact: {
        website: "https://tuscaloosainterfaithdental.org",
        email: "contact@tuscaloosainterfaithdental.org",
        phone: "(205) 555-0300"
      },
      volunteer_opportunities: true,
      accepting_board_members: true
    },
    {
      name: "Catholic Social Services - Dental Outreach",
      ein: "63-4567890",
      ntee_code: "X20",
      ntee_description: "Christian",
      mission: "Diocese of Birmingham outreach providing dental care and health services to underserved communities",
      services: [
        "Quarterly dental clinics at parish hall",
        "School dental screening partnerships",
        "Dental supply distribution",
        "Financial assistance for dental emergencies"
      ],
      annual_budget: 95000,
      families_served: 320,
      contact: {
        website: "https://cssalabama.org/dental",
        email: "dental@cssalabama.org",
        phone: "(205) 555-0400"
      },
      volunteer_opportunities: true,
      accepting_board_members: false
    }
  ];
  
  // Filter decisions based on search, topics, patterns, resources, and date range
  const filteredDecisions = exampleDecisions.filter(decision => {
    const matchesSearch = searchQuery === '' || 
      decision.decision_summary.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Map policy_domain to topic IDs
    const topicMap = {
      'health': 'public-health',
      'facilities': 'infrastructure',
      'budget': 'education' // Example mapping
    };
    const decisionTopic = topicMap[decision.policy_domain] || decision.policy_domain;
    const matchesTopic = selectedTopics.length === 0 || selectedTopics.includes(decisionTopic);
    
    // Date filtering
    const decisionDate = new Date(decision.meeting_date);
    const matchesStartDate = !startDate || decisionDate >= new Date(startDate);
    const matchesEndDate = !endDate || decisionDate <= new Date(endDate);
    
    // TODO: Add pattern matching based on decision.patterns field
    // TODO: Add resource matching based on decision.available_resources field
    
    return matchesSearch && matchesTopic && matchesStartDate && matchesEndDate;
  });

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 600, marginBottom: 8, color: '#111' }}>
          {metadata.title}
        </h1>
        <p style={{ color: '#666', fontSize: 16, lineHeight: 1.6 }}>
          {metadata.description}
        </p>
      </div>

      {/* View Mode Toggle */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16 
      }}>
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            onClick={() => setViewMode('home')}
            style={{
              padding: '10px 20px',
              borderRadius: 8,
              fontSize: 15,
              cursor: 'pointer',
              border: '1px solid',
              borderColor: viewMode === 'home' ? '#888' : '#ddd',
              background: viewMode === 'home' ? '#f5f5f2' : 'white',
              fontWeight: viewMode === 'home' ? 500 : 400,
              color: viewMode === 'home' ? '#111' : '#666',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            <Home size={14} />
            Home
          </button>
          <button
            onClick={() => setViewMode('browse')}
            style={{
              padding: '10px 20px',
              borderRadius: 8,
              fontSize: 15,
              cursor: 'pointer',
              border: '1px solid',
              borderColor: viewMode === 'browse' ? '#888' : '#ddd',
              background: viewMode === 'browse' ? '#f5f5f2' : 'white',
              fontWeight: viewMode === 'browse' ? 500 : 400,
              color: viewMode === 'browse' ? '#111' : '#666',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            <Grid size={14} />
            Explore Decisions
          </button>
        </div>
      </div>

      {/* Filters (show in browse view) */}
      {viewMode === 'browse' && (
        <TopicNavigation
          selectedTopics={selectedTopics}
          selectedPatterns={selectedPatterns}
          selectedResources={selectedResources}
          startDate={startDate}
          endDate={endDate}
          onTopicToggle={handleTopicToggle}
          onPatternToggle={handlePatternToggle}
          onResourceToggle={handleResourceToggle}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onClearAll={handleClearFilters}
        />
      )}

      {/* Content */}
      {viewMode === 'home' ? (
        <HomePage 
          onPersonaSelect={handlePersonaSelect}
          onTopicSelect={handleTopicSelect}
        />
      ) : viewMode === 'impact' ? (
        <div style={{ 
          background: 'white', 
          border: '1px solid #eee', 
          borderRadius: 12, 
          padding: '1.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}>
          <button
            onClick={handleBackToHome}
            style={{
              fontSize: 13,
              color: '#666',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 4
            }}
          >
            ← Back to Home
          </button>
          <ImpactDashboard persona={selectedPersona} topic={selectedTopic} />
        </div>
      ) : viewMode === 'split-screen' ? (
        <div style={{ 
          background: 'white', 
          border: '1px solid #eee', 
          borderRadius: 12, 
          padding: '1.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}>
          <button
            onClick={() => setViewMode('browse')}
            style={{
              fontSize: 13,
              color: '#666',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 4
            }}
          >
            ← Back to Decisions
          </button>
          <div style={{
            fontSize: 12,
            fontWeight: 600,
            color: '#059669',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: 8
          }}>
            Split-Screen Analysis
          </div>
          <h2 style={{
            fontSize: 22,
            fontWeight: 600,
            color: '#111',
            marginBottom: 16
          }}>
            Government Decision ↔ Community Response
          </h2>
          <SplitScreenView 
            decision={selectedDecision} 
            nonprofits={exampleNonprofits}
          />
        </div>
      ) : (
        <div style={{
          background: 'white',
          border: '1px solid #eee',
          borderRadius: 12,
          padding: '1.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}>
          <h2 style={{
            fontSize: 20,
            fontWeight: 500,
            marginBottom: 16
          }}>
            Explore Decisions
          </h2>
          
          {filteredDecisions.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '3rem',
              color: '#999'
            }}>
              <p style={{ fontSize: 16, marginBottom: 8 }}>
                No decisions match your filters
              </p>
              <button
                onClick={handleClearFilters}
                style={{
                  fontSize: 15,
                  color: '#D85A30',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <>
              <div style={{ fontSize: 15, color: '#888', marginBottom: 16 }}>
                Showing {filteredDecisions.length} decision{filteredDecisions.length !== 1 ? 's' : ''}
              </div>
              {filteredDecisions.map((decision, i) => (
                <DecisionCard
                  key={i}
                  decision={decision}
                  onClick={() => handleDecisionClick(decision)}
                />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
