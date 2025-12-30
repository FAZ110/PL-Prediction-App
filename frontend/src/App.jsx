import { useState } from 'react'
import './App.css'
import MatchesGrid from './components/MatchesGrid'
import UpdateMatches from './components/UpdateMatches'
import LeagueTable from './components/LeagueTable'
import Info from './components/Info'
import Footer from './components/Footer'

function App() {
  

  return (
    <div className="container">
       {/* <h1 className="app-title">⚽ Premier League AI Predictor</h1> */}

        <div className="tools">
          <UpdateMatches/>
          <Info/>
        </div>
       
       
       <div className="main-layout">
           
           <div className='matches-grid-wrapper'>
               <MatchesGrid />
           </div>

           <div className='league-table-wrapper'>
               <LeagueTable />
           </div>

       </div>
       <Footer/>

    </div>
    
  )
}

export default App
