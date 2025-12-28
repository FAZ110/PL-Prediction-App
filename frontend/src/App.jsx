import { useState } from 'react'
import './App.css'
import MatchesGrid from './components/MatchesGrid'
import UpdateMatches from './components/UpdateMatches'
import LeagueTable from './components/LeagueTable'

function App() {
  

  return (
    <div className="container">
       {/* <h1 className="app-title">⚽ Premier League AI Predictor</h1> */}

       <UpdateMatches/>
       
       {/* Create a layout wrapper */}
       <div className="main-layout">
           
           {/* Left Side: Matches (Takes up more space) */}
           <div className='matches-grid-wrapper'>
               <MatchesGrid />
           </div>

           {/* Right Side: Table (Takes up less space) */}
           <div className='league-table-wrapper'>
               <LeagueTable />
           </div>

       </div>
    </div>
    
  )
}

export default App
