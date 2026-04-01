import { useState } from 'react'
import LandingPage from './components/LandingPage'
import DashboardPage from './components/DashboardPage'
import StudioPage from './components/StudioPage'
import SignInPage from './components/SignInPage'
import SignUpPage from './components/SignUpPage'
import './index.css'

function App() {
  const [currentPage, setCurrentPage] = useState('landing')
  const [user, setUser] = useState(null)

  const handleLogin = (userData) => {
    setUser(userData)
    setCurrentPage('dashboard')
  }

  const handleRegister = (userData) => {
    setUser(userData)
    setCurrentPage('dashboard')
  }

  const handleLogout = () => {
    setUser(null)
    setCurrentPage('landing')
  }

  return (
    <div className="min-h-screen bg-surface">
      {currentPage === 'landing' && (
        <LandingPage 
          onLaunch={() => setCurrentPage('dashboard')} 
          onSignIn={() => setCurrentPage('signin')}
          onSignUp={() => setCurrentPage('signup')}
        />
      )}
      
      {currentPage === 'signin' && (
        <SignInPage 
          onHome={() => setCurrentPage('landing')} 
          onLogin={handleLogin}
          onSignUp={() => setCurrentPage('signup')}
        />
      )}

      {currentPage === 'signup' && (
        <SignUpPage 
          onHome={() => setCurrentPage('landing')} 
          onSignIn={() => setCurrentPage('signin')}
          onRegister={handleRegister}
        />
      )}

      {currentPage === 'dashboard' && (
        <DashboardPage 
          user={user}
          onNewProject={() => setCurrentPage('studio')} 
          onOpenStudio={() => setCurrentPage('studio')}
          onHome={handleLogout}
        />
      )}

      {currentPage === 'studio' && (
        <StudioPage 
          user={user}
          onBack={() => setCurrentPage('dashboard')} 
          onHome={() => setCurrentPage('landing')}
        />
      )}
    </div>
  )
}

export default App
