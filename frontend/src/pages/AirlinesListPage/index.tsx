import {Button, Col, Container, Form, Input, Row} from "reactstrap";
import {T_Airline} from "src/modules/types.ts";
import AirlineCard from "components/AirlineCard";
import {AirlineMocks} from "src/modules/mocks.ts";
import {FormEvent, useEffect} from "react";
import * as React from "react";

type Props = {
    airlines: T_Airline[],
    setAirlines: React.Dispatch<React.SetStateAction<T_Airline[]>>
    isMock: boolean,
    setIsMock: React.Dispatch<React.SetStateAction<boolean>>
    airlineName: string,
    setAirlineName: React.Dispatch<React.SetStateAction<string>>
}

const AirlinesListPage = ({airlines, setAirlines, isMock, setIsMock, airlineName, setAirlineName}:Props) => {

    const fetchData = async () => {
        try {
            const response = await fetch(`/api/airlines/?airline_name=${airlineName.toLowerCase()}`)
            const data = await response.json()
            setAirlines(data.airlines)
            setIsMock(false)
        } catch {
            createMocks()
        }
    }

    const createMocks = () => {
        setIsMock(true)
        setAirlines(AirlineMocks.filter(airline => airline.name.toLowerCase().includes(airlineName.toLowerCase())))
    }

    const handleSubmit = async (e:FormEvent) => {
        e.preventDefault()
        if (isMock) {
            createMocks()
        } else {
            await fetchData()
        }
    }

    useEffect(() => {
        fetchData()
    }, []);

    return (
        <Container>
            <Row className="mb-5">
                <Col md="6">
                    <Form onSubmit={handleSubmit}>
                        <Row>
                            <Col md="8">
                                <Input value={airlineName} onChange={(e) => setAirlineName(e.target.value)} placeholder="Поиск..."></Input>
                            </Col>
                            <Col>
                                <Button color="primary" className="w-100 search-btn">Поиск</Button>
                            </Col>
                        </Row>
                    </Form>
                </Col>
            </Row>
            <Row>
                {airlines?.map(airline => (
                    <Col key={airline.id} xs="4">
                        <AirlineCard airline={airline} isMock={isMock} />
                    </Col>
                ))}
            </Row>
        </Container>
    );
};

export default AirlinesListPage