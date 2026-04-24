import React, { useState } from 'react';
import { Filter, Video, FileText, DollarSign, BarChart3 } from 'lucide-react';

/**
 * TopicNavigation Component
 * Primary and secondary filters for browsing decisions
 */
export default function TopicNavigation({ 
  selectedTopics = [],
  selectedPatterns = [],
  selectedResources = [],
  onTopicToggle,
  onPatternToggle,
  onResourceToggle,
  onClearAll
}) {
  const [showFilters, setShowFilters] = useState(true);
  
  const topics = [
    { id: 'public-health', label: 'Public Health', sublabel: 'Dental, Water, Mental Health', color: '#1D9E75' },
    { id: 'education', label: 'Education & Youth', sublabel: 'School Board, Pre-K', color: '#185FA5' },
    { id: 'infrastructure', label: 'Infrastructure', sublabel: 'Roads, Utilities, Construction', color: '#BA7517' },
    { id: 'public-safety', label: 'Public Safety', sublabel: 'Police, Fire, EMS', color: '#E24B4A' }
  ];
  
  const patterns = [
    { id: 'technocratic-veto', label: 'Technocratic Veto', description: 'Legal/risk managers blocking decisions' },
    { id: 'sequential-deferral', label: 'Sequential Deferral', description: 'Repeated "tabling for study"' },
    { id: 'performance-rationale', label: 'Performance Rationale', description: 'Rhetoric not matching funding' }
  ];
  
  const resources = [
    { id: 'video', label: 'Video Recap', icon: Video },
    { id: 'budget', label: 'Budget PDF', icon: DollarSign },
    { id: 'dashboard', label: 'Impact Dashboard', icon: BarChart3 },
    { id: 'summary', label: 'Summary Notes', icon: FileText }
  ];
  
  const hasActiveFilters = selectedTopics.length > 0 || selectedPatterns.length > 0 || selectedResources.length > 0;
  
  return (
    <div style={{ marginBottom: 20 }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12
      }}>
        <button
          onClick={() => setShowFilters(!showFilters)}
          style={{
            padding: '8px 16px',
            border: '1px solid',
            borderColor: showFilters ? '#888' : '#ddd',
            borderRadius: 8,
            background: showFilters ? '#f5f5f2' : 'white',
            cursor: 'pointer',
            fontSize: 13,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            color: showFilters ? '#222' : '#666'
          }}
        >
          <Filter size={14} />
          Filter & Browse
          {hasActiveFilters && (
            <span style={{
              background: '#D85A30',
              color: 'white',
              borderRadius: '50%',
              width: 18,
              height: 18,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 10,
              fontWeight: 600
            }}>
              {selectedTopics.length + selectedPatterns.length + selectedResources.length}
            </span>
          )}
        </button>
        
        {hasActiveFilters && (
          <button
            onClick={onClearAll}
            style={{
              padding: '8px 16px',
              border: '1px solid #ddd',
              borderRadius: 8,
              background: 'white',
              cursor: 'pointer',
              fontSize: 13,
              color: '#D85A30'
            }}
          >
            Clear All Filters
          </button>
        )}
      </div>
      
      {/* Filter Panel */}
      {showFilters && (
        <div style={{
          background: '#f5f5f2',
          borderRadius: 12,
          padding: 18,
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr',
          gap: 20
        }}>
          {/* Primary Navigation: Topics */}
          <div>
            <div style={{
              fontSize: 12,
              fontWeight: 500,
              color: '#666',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 12
            }}>
              Primary Topic / Domain
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {topics.map(topic => {
                const isSelected = selectedTopics.includes(topic.id);
                return (
                  <button
                    key={topic.id}
                    onClick={() => onTopicToggle(topic.id)}
                    style={{
                      padding: '10px 14px',
                      borderRadius: 8,
                      border: '2px solid',
                      borderColor: isSelected ? topic.color : '#ddd',
                      background: isSelected ? `${topic.color}15` : 'white',
                      color: '#222',
                      fontSize: 13,
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontWeight: isSelected ? 500 : 400,
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div style={{ fontWeight: 500 }}>{topic.label}</div>
                    <div style={{ fontSize: 11, color: '#888', marginTop: 2 }}>
                      {topic.sublabel}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Secondary Filter: Patterns */}
          <div>
            <div style={{
              fontSize: 12,
              fontWeight: 500,
              color: '#666',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 12
            }}>
              Filter by Pattern
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {patterns.map(pattern => {
                const isSelected = selectedPatterns.includes(pattern.id);
                return (
                  <label
                    key={pattern.id}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 8,
                      padding: 8,
                      borderRadius: 6,
                      background: isSelected ? 'white' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background 0.2s ease'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onPatternToggle(pattern.id)}
                      style={{ marginTop: 2 }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 12, fontWeight: 500, color: '#222' }}>
                        {pattern.label}
                      </div>
                      <div style={{ fontSize: 10, color: '#888', marginTop: 2 }}>
                        {pattern.description}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
          
          {/* Tertiary Filter: Resources */}
          <div>
            <div style={{
              fontSize: 12,
              fontWeight: 500,
              color: '#666',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 12
            }}>
              Filter by Resource
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {resources.map(resource => {
                const isSelected = selectedResources.includes(resource.id);
                const Icon = resource.icon;
                return (
                  <label
                    key={resource.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: 8,
                      borderRadius: 6,
                      background: isSelected ? 'white' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background 0.2s ease'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => onResourceToggle(resource.id)}
                    />
                    <Icon size={14} color={isSelected ? '#D85A30' : '#888'} />
                    <div style={{ 
                      fontSize: 12, 
                      color: isSelected ? '#222' : '#666',
                      fontWeight: isSelected ? 500 : 400
                    }}>
                      {resource.label}
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        </div>
      )}
      
      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div style={{
          marginTop: 12,
          display: 'flex',
          flexWrap: 'wrap',
          gap: 6,
          alignItems: 'center'
        }}>
          <span style={{ fontSize: 11, color: '#888' }}>Active filters:</span>
          {selectedTopics.map(topicId => {
            const topic = topics.find(t => t.id === topicId);
            return (
              <span
                key={topicId}
                style={{
                  fontSize: 11,
                  padding: '4px 10px',
                  borderRadius: 12,
                  background: topic.color,
                  color: 'white',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
              >
                {topic.label}
                <button
                  onClick={() => onTopicToggle(topicId)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    padding: 0,
                    fontSize: 14,
                    lineHeight: 1
                  }}
                >
                  ×
                </button>
              </span>
            );
          })}
          {selectedPatterns.map(patternId => {
            const pattern = patterns.find(p => p.id === patternId);
            return (
              <span
                key={patternId}
                style={{
                  fontSize: 11,
                  padding: '4px 10px',
                  borderRadius: 12,
                  background: '#BA7517',
                  color: 'white',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
              >
                {pattern.label}
                <button
                  onClick={() => onPatternToggle(patternId)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    padding: 0,
                    fontSize: 14,
                    lineHeight: 1
                  }}
                >
                  ×
                </button>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
