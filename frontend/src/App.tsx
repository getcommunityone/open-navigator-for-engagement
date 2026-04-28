import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import HomeModern from './pages/HomeModern'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Heatmap from './pages/Heatmap'
import Documents from './pages/Documents'
import Opportunities from './pages/Opportunities'
import Nonprofits from './pages/Nonprofits'
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

function App() {
  return (
    <Routes>
      {/* Modern home page without Layout (has its own header) */}
      <Route path="/" element={<HomeModern />} />
      
      {/* Classic home page (if needed) */}
      <Route path="/classic" element={<Layout />}>
        <Route index element={<Home />} />
      </Route>
      
      {/* All other pages with sidebar layout */}
      <Route path="/" element={<Layout />}>
        <Route path="explore" element={<Explore />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="people" element={<PeopleFinder />} />
        <Route path="heatmap" element={<Heatmap />} />
        <Route path="documents" element={<Documents />} />
        <Route path="opportunities" element={<Opportunities />} />
        <Route path="nonprofits" element={<Nonprofits />} />
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
    </Routes>
  )
}

export default App
