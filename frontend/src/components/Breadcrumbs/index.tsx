import {Breadcrumb, BreadcrumbItem} from "reactstrap";
import {Link, useLocation} from "react-router-dom";
import {T_Airline} from "modules/types.ts";

interface Props {
    selectedAirline: T_Airline | null
}

const Breadcrumbs = ({ selectedAirline }: Props) => {

    const location = useLocation()

    return (
        <Breadcrumb className="fs-5">
			{location.pathname == "/" &&
				<BreadcrumbItem>
					<Link to="/">
						Главная
					</Link>
				</BreadcrumbItem>
			}
			{location.pathname.includes("/airlines") &&
                <BreadcrumbItem active>
                    <Link to="/airlines">
						Авиакомпании
                    </Link>
                </BreadcrumbItem>
			}
            {selectedAirline &&
                <BreadcrumbItem active>
                    <Link to={location.pathname}>
                        { selectedAirline.name }
                    </Link>
                </BreadcrumbItem>
            }
			<BreadcrumbItem />
        </Breadcrumb>
    );
};

export default Breadcrumbs