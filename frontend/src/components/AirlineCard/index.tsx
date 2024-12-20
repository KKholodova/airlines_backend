import {Button, Card, CardBody, CardImg, CardText, CardTitle} from "reactstrap";
import mockImage from "assets/mock.png";
import {Link} from "react-router-dom";
import {T_Airline} from "modules/types.ts";

interface AirlineCardProps {
    airline: T_Airline,
    isMock: boolean
}

const AirlineCard = ({airline, isMock}: AirlineCardProps) => {
    return (
        <Card key={airline.id} style={{width: '18rem', margin: "0 auto 50px", height: "calc(100% - 50px)" }}>
            <CardImg
                src={isMock ? mockImage as string : airline.image}
                style={{"height": "200px"}}
            />
            <CardBody className="d-flex flex-column justify-content-between">
                <CardTitle tag="h5">
                    {airline.name}
                </CardTitle>
                <CardText>
                    Год основания: {airline.foundation_date}
                </CardText>
                <Link to={`/airlines/${airline.id}`}>
                    <Button color="primary">
                        Открыть
                    </Button>
                </Link>
            </CardBody>
        </Card>
    );
};

export default AirlineCard