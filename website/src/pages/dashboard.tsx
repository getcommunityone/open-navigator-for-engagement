import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';

export default function DashboardRedirect(): JSX.Element {
  return (
    <Layout title="Dashboard" description="Access the Open Navigator Dashboard">
      <div className="container margin-vert--lg">
        <Heading as="h1">📊 Open Navigator Dashboard</Heading>
        
        <div className="alert alert--info margin-vert--md">
          <p>
            The interactive dashboard is a separate React application that provides
            real-time access to advocacy opportunities, meeting minutes, and nonprofit data.
          </p>
        </div>

        <div className="card margin-vert--lg">
          <div className="card__header">
            <Heading as="h3">Development Access</Heading>
          </div>
          <div className="card__body">
            <p>To access the dashboard in development mode:</p>
            <ol>
              <li>
                <strong>Start the API backend:</strong>
                <pre>
                  <code>
{`source .venv/bin/activate
python main.py serve`}
                  </code>
                </pre>
              </li>
              <li>
                <strong>Start the React frontend:</strong>
                <pre>
                  <code>
{`cd frontend
npm install
npm run dev`}
                  </code>
                </pre>
              </li>
              <li>
                <strong>Access the dashboard:</strong> <a href="http://localhost:3000" target="_blank">http://localhost:3000</a>
              </li>
            </ol>
          </div>
        </div>

        <div className="card margin-vert--lg">
          <div className="card__header">
            <Heading as="h3">Production Deployment</Heading>
          </div>
          <div className="card__body">
            <p>For production deployments, see:</p>
            <ul>
              <li><Link to="/docs/deployment/databricks">Databricks Apps Deployment</Link></li>
              <li><Link to="/docs/deployment/docker">Docker Deployment</Link></li>
            </ul>
          </div>
        </div>

        <div className="card margin-vert--lg">
          <div className="card__header">
            <Heading as="h3">Dashboard Features</Heading>
          </div>
          <div className="card__body">
            <div className="row">
              <div className="col col--6">
                <ul>
                  <li>📊 <strong>Analytics Dashboard</strong> - Real-time opportunity tracking</li>
                  <li>🗺️ <strong>Interactive Heatmap</strong> - Geographic visualization</li>
                  <li>📄 <strong>Document Explorer</strong> - Search meeting minutes</li>
                </ul>
              </div>
              <div className="col col--6">
                <ul>
                  <li>🔔 <strong>Opportunities</strong> - Identified advocacy windows</li>
                  <li>🏛️ <strong>Nonprofit Search</strong> - Find local organizations</li>
                  <li>⚙️ <strong>Settings</strong> - Configure alerts and preferences</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="margin-vert--lg text--center">
          <Link
            className="button button--primary button--lg"
            href="http://localhost:3000"
            target="_blank">
            Open Dashboard (Dev Mode) →
          </Link>
          <Link
            className="button button--secondary button--lg margin-left--md"
            to="/docs/dashboard">
            Read Documentation
          </Link>
        </div>
      </div>
    </Layout>
  );
}
