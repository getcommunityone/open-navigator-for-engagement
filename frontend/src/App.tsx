import { Routes, Route, Navigate, useParams, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import HomeModern from './pages/HomeModern'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Heatmap from './pages/Heatmap'
import Documents from './pages/Documents'
import Opportunities from './pages/Opportunities'
import Nonprofits from './pages/Nonprofits'
import NonprofitsHF from './pages/NonprofitsHF'
import Settings from './pages/Settings'
import PeopleFinder from './pages/PeopleFinder'
import DebateFinder from './pages/DebateGrader'
import Profile from './pages/Profile'
import Explore from './pages/Explore'
import Events from './pages/Events'
import Services from './pages/Services'
import Developers from './pages/Developers'
import Hackathons from './pages/Hackathons'
import OpenSource from './pages/OpenSource'
import AdvocacyTopics from './pages/AdvocacyTopics'
import FactChecking from './pages/FactChecking'
import UnifiedSearch from './pages/UnifiedSearch'
import JurisdictionsSearch from './pages/JurisdictionsSearch'
import PolicyMap from './pages/PolicyMap'
import CensusMapPage from './pages/CensusMapPage'
import BillDetail from './pages/BillDetail'
import NotFound from './pages/NotFound'

/** Old bookmarked URLs used `/census-map/county/...`; national view is now state-level at `/census-map/us/...`. */
function CensusCountyAliasRedirect() {
  const { vintage, metric } = useParams<{ vintage: string; metric: string }>()
  const { search } = useLocation()
  const v = vintage ?? '2022'
  const m = metric ?? 'median_household_income'
  return <Navigate to={`/census-map/us/${v}/${m}${search}`} replace />
}

function App() {
  return (
    <Routes>
      {/* Ground News-style homepage without Layout (has its own header) */}
      <Route path="/" element={<Home />} />
      
      {/* Old modern home page (if needed) */}
      <Route path="/classic" element={<Layout />}>
        <Route index element={<HomeModern />} />
      </Route>
      
      {/* All other pages with sidebar layout */}
      <Route path="/" element={<Layout />}>
        <Route path="explore" element={<Explore />} />
        <Route path="search" element={<UnifiedSearch />} />
        <Route path="jurisdictions" element={<JurisdictionsSearch />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="people" element={<PeopleFinder />} />
        <Route path="heatmap" element={<Heatmap />} />
        <Route path="policy-map" element={<PolicyMap />} />
        <Route
          path="census-map"
          element={<Navigate to="/census-map/us/2022/median_household_income" replace />}
        />
        <Route path="census-map/us/:vintage/:metric" element={<CensusMapPage />} />
        <Route path="census-map/state/:stateFips/:vintage/:metric" element={<CensusMapPage />} />
        <Route
          path="census-map/county/:vintage/:metric"
          element={<CensusCountyAliasRedirect />}
        />
        <Route path="census-map/place/:stateFips/:vintage/:metric" element={<CensusMapPage />} />
        <Route path="bill/:billId" element={<BillDetail />} />
        <Route path="documents" element={<Documents />} />
        <Route path="opportunities" element={<Opportunities />} />
        <Route path="nonprofits" element={<Nonprofits />} />
        <Route path="nonprofits-hf" element={<NonprofitsHF />} />
        <Route path="debate-grader" element={<DebateFinder />} />
        <Route path="profile" element={<Profile />} />
        <Route path="settings" element={<Settings />} />
        <Route path="events" element={<Events />} />
        <Route path="services" element={<Services />} />
        <Route path="developers" element={<Developers />} />
        <Route path="hackathons" element={<Hackathons />} />
        <Route path="opensource" element={<OpenSource />} />
        <Route path="advocacy-topics" element={<AdvocacyTopics />} />
        <Route path="fact-checking" element={<FactChecking />} />
      </Route>
      
      {/* 404 Page - Catch all unmatched routes */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
