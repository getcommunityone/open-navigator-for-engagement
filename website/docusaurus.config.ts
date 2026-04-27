import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Open Navigator for Engagement',
  tagline: 'Find opportunities in local meetings and budgets',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://opennavigator.org',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  // For HuggingFace Spaces, docs are served from /docs/ subdirectory
  baseUrl: process.env.DOCUSAURUS_BASE_URL || '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'getcommunityone', // Usually your GitHub org/user name.
  projectName: 'oral-health-policy-pulse', // Usually your repo name.

  onBrokenLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/', // Serve docs at root since nginx handles /docs/ prefix
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/getcommunityone/open-navigator-for-engagement/tree/main/website/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/getcommunityone/open-navigator-for-engagement/tree/main/website/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: ['@docusaurus/theme-mermaid'],

  markdown: {
    mermaid: true,
  },

  themeConfig: {
    mermaid: {
      theme: { light: 'default', dark: 'dark' },
      options: {
        fontSize: 18,
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        entityPadding: 20,
        minEntityHeight: 120,
        minEntityWidth: 180,
      },
    },
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Open Navigator Home',
      logo: {
        alt: 'CommunityOne Logo',
        src: 'img/communityone_logo.svg',
        href: 'http://localhost:5173',
        target: '_self',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'gettingStartedSidebar',
          position: 'left',
          label: 'Getting Started',
        },
        {
          type: 'docSidebar',
          sidebarId: 'policyMakersSidebar',
          position: 'left',
          label: 'Policy Makers',
        },
        {
          type: 'docSidebar',
          sidebarId: 'developersSidebar',
          position: 'left',
          label: 'Developers',
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/getcommunityone/open-navigator-for-engagement',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'Data Sources',
              to: '/docs/data-sources',
            },
            {
              label: 'API Reference',
              to: '/docs/api',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Launch Open Navigator',
              to: '/dashboard',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/getcommunityone/open-navigator-for-engagement',
            },
            {
              label: 'GroundVue (Partner)',
              href: 'https://www.groundvue.org/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'License (MIT)',
              href: 'https://github.com/getcommunityone/open-navigator-for-engagement/blob/main/LICENSE',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Community One. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
