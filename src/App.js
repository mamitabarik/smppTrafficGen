import React from "react"
import Header from "./Components/Header"
import MainCon from "./Components/MainCon"
import MainConDashboard from "./Components/MainConDashboard"
import Footer from "./Components/Footer"
import { BrowserRouter as Router, Route, Link } from "react-router-dom";



function Dashboard() {
  return (
		<div>
			<MainConDashboard />
			<Footer />
		</div>
	)
}
 
function App() {
  return (
    <Router>
      <div>
		  <Header/>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/dashboard/">Dashboard</Link>
            </li>
          </ul>
        </nav>

        <Route path="/" exact component={Home} />
        <Route path="/dashboard/" component={Dashboard} />
      </div>
    </Router>
  );
}

function Home() {
	return (
		<div>
			<MainCon />
			<Footer />
		</div>
	)
}

export default App