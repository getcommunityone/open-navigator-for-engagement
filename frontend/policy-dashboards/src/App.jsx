import React, { useState } from 'react';
import HomePage from './components/HomePage';
import ImpactDashboard from './components/ImpactDashboard';
import TopicNavigation from './components/TopicNavigation';
import DecisionCard from './components/shared/DecisionCard';
import { metadata } from './data/dashboardData';
import { Home, Grid } from 'lucide-react';

export default function App() {
  const [viewMode, setViewMode] = useState('browse'); // 'home', 'impact', 'browse'
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
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
      policy_domain: "facilities"
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
      policy_domain: "health"
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
      policy_domain: "budget"
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
                  onClick={() => console.log('View decision:', decision)}
                />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}
