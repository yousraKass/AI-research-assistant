import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Container, Navbar, Nav } from 'react-bootstrap'
import Home from './pages/Home'
import Results from './pages/Results'
import About from './pages/About'

function App() {
  return (
    <BrowserRouter>
      <Navbar bg="light" expand="lg" className="mb-4" sticky="top">
        <Container>
          <Navbar.Brand as={Link} to="/">AI Research Assistant</Navbar.Brand>
          <Navbar.Toggle aria-controls="main-nav" />
          <Navbar.Collapse id="main-nav">
            <Nav className="ms-auto">
              <Nav.Link as={Link} to="/">Home</Nav.Link>
              <Nav.Link as={Link} to="/about">About</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mb-5">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results/:jobId" element={<Results />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Container>
    </BrowserRouter>
  )
}

export default App
