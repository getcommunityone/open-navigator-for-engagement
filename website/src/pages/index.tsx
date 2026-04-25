import type {ReactNode} from 'react';
import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          🦷 {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started - 5min ⏱️
          </Link>
          <Link
            className="button button--primary button--lg margin-left--md"
            href="http://localhost:5173"
            target="_blank">
            🚀 Launch Dashboard →
          </Link>
        </div>
      </div>
    </header>
  );
}

function HomepageFeatures() {
  const features = [
    {
      title: '📄 Meeting Minutes & Financial Documents',
      description: 'Analyzes thousands of municipal meeting minutes and budget documents from 90,000+ government jurisdictions and nonprofit organizations.',
    },
    {
      title: '🤖 Multi-Agent AI System',
      description: 'Coordinated agents for scraping, parsing, classification, sentiment analysis, and advocacy generation powered by Databricks.',
    },
    {
      title: '💰 Budget-to-Minutes Analysis',
      description: 'Correlates meeting rhetoric with actual spending to reveal true priorities and identify gaps between statements and funding.',
    },
    {
      title: '🔍 Comprehensive Data Sources',
      description: 'Integrates Census data, NCES school districts, ProPublica nonprofit data, and meeting datasets. All 100% free and public.',
    },
    {
      title: '🗺️ Interactive Heatmap',
      description: 'Visual representation of policy opportunities with urgency levels, topic concentration, and clickable details.',
    },
    {
      title: '📧 Automated Advocacy Materials',
      description: 'Generates personalized emails, talking points, social media content, and policy briefs based on opportunities.',
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {features.map((feature, idx) => (
            <div key={idx} className={clsx('col col--4')}>
              <div className="text--center padding-horiz--md padding-vert--md">
                <Heading as="h3">{feature.title}</Heading>
                <p>{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HomepageStats() {
  return (
    <section className="container margin-vert--lg">
      <div className="row">
        <div className="col text--center">
          <Heading as="h2">By the Numbers</Heading>
          <p className="margin-bottom--lg">Comprehensive data coverage for evidence-based advocacy</p>
        </div>
      </div>
      <div className="row">
        <div className="col col--3 text--center">
          <div className="padding--md">
            <Heading as="h3">90,000+</Heading>
            <p>Government Jurisdictions</p>
          </div>
        </div>
        <div className="col col--3 text--center">
          <div className="padding--md">
            <Heading as="h3">13,000+</Heading>
            <p>School Districts</p>
          </div>
        </div>
        <div className="col col--3 text--center">
          <div className="padding--md">
            <Heading as="h3">3M+</Heading>
            <p>Nonprofit Organizations</p>
          </div>
        </div>
        <div className="col col--3 text--center">
          <div className="padding--md">
            <Heading as="h3">$0</Heading>
            <p>Total Cost</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function WhyItMatters() {
  return (
    <section className="container margin-vert--lg text--center">
      <Heading as="h2">Why This Matters</Heading>
      <div className="row margin-top--lg">
        <div className="col col--4 padding--md">
          <Heading as="h4">Direct Community Impact</Heading>
          <p>
            Find nonprofits and organizations already providing services, connect citizens to care, and identify partnership opportunities.
          </p>
        </div>
        <div className="col col--4 padding--md">
          <Heading as="h4">Government Accountability</Heading>
          <p>
            Challenge "impossibility" claims, expose resource gaps, and compare spending priorities with service provision.
          </p>
        </div>
        <div className="col col--4 padding--md">
          <Heading as="h4">Strategic Advocacy</Heading>
          <p>
            Ground campaigns in real data, build coalitions, and mobilize communities with evidence-based messaging.
          </p>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  
  // Show prominent modal/overlay to redirect to dashboard
  const [showModal, setShowModal] = React.useState(true);
  
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="AI-powered advocacy opportunity finder analyzing municipal meetings and financial documents">
      
      {/* URGENT: Redirect Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '3rem',
            borderRadius: '12px',
            maxWidth: '600px',
            textAlign: 'center',
          }}>
            <h2 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#000' }}>
              ⚠️ You're on the Documentation Site
            </h2>
            <p style={{ fontSize: '1.2rem', marginBottom: '1.5rem', color: '#333' }}>
              This is <strong>NOT the application</strong>. This is just documentation and guides.
            </p>
            <p style={{ fontSize: '1.2rem', marginBottom: '2rem', color: '#333' }}>
              Your original dashboard with <strong>search, filters, heatmap, and all features</strong> is at:
            </p>
            <a
              href="http://localhost:5173"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-block',
                backgroundColor: '#0ea5e9',
                color: 'white',
                padding: '1rem 2rem',
                fontSize: '1.5rem',
                fontWeight: 'bold',
                textDecoration: 'none',
                borderRadius: '8px',
                marginBottom: '1rem',
              }}
            >
              🚀 Open the Real Dashboard (Port 5173)
            </a>
            <div style={{ marginTop: '1.5rem' }}>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: 'none',
                  border: '1px solid #ccc',
                  padding: '0.5rem 1rem',
                  cursor: 'pointer',
                  color: '#666',
                }}
              >
                Stay on docs site (for reading guides)
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Important Notice Banner */}
      <div style={{
        backgroundColor: '#ef4444',
        color: 'white',
        padding: '1.5rem',
        textAlign: 'center',
        fontWeight: 'bold',
        fontSize: '1.2rem',
      }}>
        ⚠️ THIS IS THE DOCUMENTATION SITE, NOT THE APPLICATION! 
        <a 
          href="http://localhost:5173" 
          target="_blank" 
          style={{
            color: 'white',
            textDecoration: 'underline',
            marginLeft: '1rem',
            fontWeight: 'bold',
            fontSize: '1.3rem',
          }}
        >
          🚀 CLICK HERE FOR THE REAL DASHBOARD →
        </a>
      </div>

      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomepageStats />
        <WhyItMatters />
      </main>
    </Layout>
  );
}
