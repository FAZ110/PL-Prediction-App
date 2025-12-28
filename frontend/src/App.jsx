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
       
       <div className="main-layout">
           
           <div className='matches-grid-wrapper'>
               <MatchesGrid />
           </div>

           <div className='league-table-wrapper'>
               <LeagueTable />
           </div>

       </div>
    </div>
    
  )
}

export default App
