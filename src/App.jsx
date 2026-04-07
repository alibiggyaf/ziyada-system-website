import { lazy, Suspense } from 'react'
import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes, Navigate, Outlet } from 'react-router-dom';
import { AdminAuthProvider } from './admin/AdminAuthProvider';
import PageNotFound from './lib/PageNotFound';
import { Analytics } from '@vercel/analytics/react';

// Layout
import ZiyadaLayout from './components/ziyada/Layout';

// Pages
import Home from './pages/Home';
import Services from './pages/Services';
import About from './pages/About';
import Why from './pages/Why';
import Cases from './pages/Cases';
import Blog from './pages/Blog';
import BlogPost from './pages/BlogPost';
import BookMeeting from './pages/BookMeeting';
import RequestProposal from './pages/RequestProposal';
import Contact from './pages/Contact';
import ThankYou from './pages/ThankYou';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import ServiceAutomation from './pages/ServiceAutomation';
import ServiceCRM from './pages/ServiceCRM';
import ServiceLeadGen from './pages/ServiceLeadGen';
import ServiceMarketing from './pages/ServiceMarketing';
import ServiceWebDev from './pages/ServiceWebDev';
import ServiceSocial from './pages/ServiceSocial';
import FAQ from './pages/FAQ';

// Admin (lazy-loaded)
const AdminLogin = lazy(() => import('./admin/AdminLogin'));
const ResetPassword = lazy(() => import('./admin/ResetPassword'));
const AdminLayout = lazy(() => import('./admin/AdminLayout'));
const AdminAuthGuard = lazy(() => import('./admin/AdminAuthGuard'));
const DashboardHome = lazy(() => import('./admin/pages/DashboardHome'));
const LeadsManager = lazy(() => import('./admin/pages/LeadsManager'));
const BookingsManager = lazy(() => import('./admin/pages/BookingsManager'));
const BlogManager = lazy(() => import('./admin/pages/BlogManager'));
const BlogEditor = lazy(() => import('./admin/pages/BlogEditor'));
const CasesManager = lazy(() => import('./admin/pages/CasesManager'));
const FAQManager = lazy(() => import('./admin/pages/FAQManager'));
const ServicesManager = lazy(() => import('./admin/pages/ServicesManager'));
const SubscribersManager = lazy(() => import('./admin/pages/SubscribersManager'));
const AnalyticsSummary = lazy(() => import('./admin/pages/AnalyticsSummary'));
const SettingsPanel = lazy(() => import('./admin/pages/SettingsPanel'));
const YouTubeTrendsDashboard = lazy(() => import('./pages/YouTubeTrendsDashboard'));
const CompetitorDashboard = lazy(() => import('./admin/pages/CompetitorDashboard'));

const AdminFallback = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0f172a' }}>
    <div style={{ color: '#94a3b8', fontSize: '14px' }}>Loading...</div>
  </div>
);

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/Home" replace />} />

      {/* Public site with shared layout */}
      <Route element={<ZiyadaLayout />}>
        <Route path="/Home" element={<Home />} />
        <Route path="/Services" element={<Services />} />
        <Route path="/About" element={<About />} />
        <Route path="/Why" element={<Why />} />
        <Route path="/Cases" element={<Cases />} />
        <Route path="/Blog" element={<Blog />} />
        <Route path="/BlogPost" element={<BlogPost />} />
        <Route path="/blog/:slug" element={<BlogPost />} />
        <Route path="/BookMeeting" element={<BookMeeting />} />
        <Route path="/RequestProposal" element={<RequestProposal />} />
        <Route path="/Contact" element={<Contact />} />
        <Route path="/ThankYou" element={<ThankYou />} />
        <Route path="/Privacy" element={<Privacy />} />
        <Route path="/Terms" element={<Terms />} />
        <Route path="/Services/automation" element={<ServiceAutomation />} />
        <Route path="/Services/crm" element={<ServiceCRM />} />
        <Route path="/Services/lead-generation" element={<ServiceLeadGen />} />
        <Route path="/Services/marketing" element={<ServiceMarketing />} />
        <Route path="/Services/web-development" element={<ServiceWebDev />} />
        <Route path="/Services/seo-sem" element={<Navigate to="/Services/marketing" replace />} />
        <Route path="/Services/social-media" element={<ServiceSocial />} />
        <Route path="/FAQ" element={<FAQ />} />
      </Route>

      {/* Backward compatibility redirects */}
      <Route path="/AdminDashboard" element={<Navigate to="/admin" replace />} />
      <Route path="/trend-intelligence" element={<Navigate to="/admin/trends" replace />} />
      <Route path="/youtube-trends" element={<Navigate to="/admin/trends" replace />} />

      {/* Admin Panel — wrapped in AdminAuthProvider */}
      <Route element={<Suspense fallback={<AdminFallback />}><AdminAuthProvider><Outlet /></AdminAuthProvider></Suspense>}>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/reset-password" element={<ResetPassword />} />
        <Route path="/admin" element={<AdminAuthGuard />}>
          <Route element={<AdminLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="leads" element={<LeadsManager />} />
            <Route path="bookings" element={<BookingsManager />} />
            <Route path="blog" element={<BlogManager />} />
            <Route path="blog/new" element={<BlogEditor />} />
            <Route path="blog/edit/:id" element={<BlogEditor />} />
            <Route path="cases" element={<CasesManager />} />
            <Route path="faq" element={<FAQManager />} />
            <Route path="services" element={<ServicesManager />} />
            <Route path="subscribers" element={<SubscribersManager />} />
            <Route path="analytics" element={<AnalyticsSummary />} />
            <Route path="settings" element={<SettingsPanel />} />
            <Route path="trends" element={<YouTubeTrendsDashboard />} />
            <Route path="competitor" element={<CompetitorDashboard />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<PageNotFound />} />
    </Routes>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClientInstance}>
      <Router>
        <AppRoutes />
      </Router>
      <Toaster />
      <Analytics />
    </QueryClientProvider>
  )
}

export default App
