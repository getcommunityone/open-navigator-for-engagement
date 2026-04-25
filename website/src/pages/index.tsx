import type {ReactNode} from 'react';
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
            to="/dashboard">
            Open Dashboard →
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
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="AI-powered advocacy opportunity finder analyzing municipal meetings and financial documents">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <HomepageStats />
        <WhyItMatters />
      </main>
    </Layout>
  );
}
