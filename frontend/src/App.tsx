import {useState} from "react";
import Header from "components/Header";
import Breadcrumbs from "components/Breadcrumbs";
import AirlinePage from "pages/AirlinePage";
import AirlinesListPage from "pages/AirlinesListPage";
import {Route, Routes} from "react-router-dom";
import {T_Airline} from "src/modules/types.ts";
import {Container, Row} from "reactstrap";
import HomePage from "pages/HomePage";
import "./styles.css"

function App() {

    const [airlines, setAirlines] = useState<T_Airline[]>([])

    const [selectedAirline, setSelectedAirline] = useState<T_Airline | null>(null)

    const [isMock, setIsMock] = useState(false);

    const [airlineName, setAirlineName] = useState<string>("")

    return (
        <div>
            <Header/>
            <Container className="pt-4">
                <Row className="mb-3">
                    <Breadcrumbs selectedAirline={selectedAirline} />
                </Row>
                <Row>
                    <Routes>
						<Route path="/" element={<HomePage />} />
                        <Route path="/airlines/" element={<AirlinesListPage airlines={airlines} setAirlines={setAirlines} isMock={isMock} setIsMock={setIsMock} airlineName={airlineName} setAirlineName={setAirlineName}/>} />
                        <Route path="/airlines/:id" element={<AirlinePage selectedAirline={selectedAirline} setSelectedAirline={setSelectedAirline} isMock={isMock} setIsMock={setIsMock}/>} />
                    </Routes>
                </Row>
            </Container>
        </div>
    )
}

export default App
