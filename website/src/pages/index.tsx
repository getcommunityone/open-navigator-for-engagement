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
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
          <img 
            src="/img/communityone_logo.jpg" 
            alt="CommunityOne Logo" 
            style={{ height: '80px', marginRight: '1rem' }}
          />
          <Heading as="h1" className="hero__title" style={{ margin: 0 }}>
            {siteConfig.title}
          </Heading>
        </div>
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
      description: 'Tracks what happens in local meetings and budgets. Covers 90,000+ cities, counties, and school districts.',
    },
    {
      title: '🤖 Automated Analysis',
      description: 'Finds documents. Reads them. Identifies topics. Spots opportunities. Drafts emails.',
    },
    {
      title: '💰 Words vs Money',
      description: 'Compare what they say in meetings with what they actually spend. Find the gaps.',
    },
    {
      title: '🔍 Free Public Data',
      description: 'Census, school district, and nonprofit data. All free. All public.',
    },
    {
      title: '🗺️ Visual Map',
      description: 'See opportunities on a map. Filter by topic and urgency. Click for details.',
    },
    {
      title: '📧 Draft Materials',
      description: 'Auto-generate emails, talking points, and social posts for each opportunity.',
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
          <Heading as="h2">Coverage</Heading>
          <p className="margin-bottom--lg">Scale of available data</p>
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
  
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Find opportunities in local meetings and budgets">
      
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomepageStats />
        <WhyItMatters />
      </main>
    </Layout>
  );
}
