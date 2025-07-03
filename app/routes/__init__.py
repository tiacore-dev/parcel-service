from fastapi import FastAPI
from tiacore_lib.routes.auth_route import auth_router
from tiacore_lib.routes.company_route import company_router
from tiacore_lib.routes.invite_route import invite_router
from tiacore_lib.routes.register_route import register_router
from tiacore_lib.routes.role_route import role_router
from tiacore_lib.routes.user_route import user_router

from .arrival_warehouse_route import arrival_to_warehouse_router
from .delivery_route import delivery_router
from .issue_to_employee import issue_to_employee_router
from .parcel_cargo_route import parcel_cargo_router
from .parcel_product_route import parcel_product_router
from .parcel_route import parcel_router
from .parcel_status_route import parcel_status_router
from .pickup_route import pickup_router
from .return_route import return_router
from .statuses_route import status_router
from .transit_detail_route import transit_details_router
from .transit_route import transit_router


def register_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(invite_router, prefix="/api", tags=["Invite"])
    app.include_router(register_router, prefix="/api", tags=["Register"])
    app.include_router(user_router, prefix="/api/users", tags=["Users"])
    app.include_router(company_router, prefix="/api/companies", tags=["Companies"])
    app.include_router(role_router, prefix="/api/roles", tags=["Roles"])

    app.include_router(parcel_router, prefix="/api/parcels", tags=["Parcels"])
    app.include_router(
        parcel_cargo_router, prefix="/api/parcel-cargo", tags=["ParcelCargo"]
    )
    app.include_router(
        parcel_product_router, prefix="/api/parcel-products", tags=["ParcelProducts"]
    )
    app.include_router(
        parcel_status_router, prefix="/api/parcel-status", tags=["ParcelStatus"]
    )
    app.include_router(status_router, prefix="/api/statuses", tags=["StatusEnum"])
    app.include_router(
        pickup_router,
        prefix="/api/pickup-from-sender",
        tags=["Pickup"],
    )
    app.include_router(
        delivery_router,
        prefix="/api/delivery-to-recipient",
        tags=["DeliveryToRecipient"],
    )
    app.include_router(return_router, prefix="/api/return", tags=["Return"])
    app.include_router(
        arrival_to_warehouse_router,
        prefix="/api/arrival-to-warehouse",
        tags=["ArrivalToWarehouse"],
    )
    app.include_router(
        issue_to_employee_router,
        prefix="/api/issue-to-employee",
        tags=["IssueToEmployee"],
    )
    app.include_router(transit_router, prefix="/api/transit", tags=["Transit"])
    app.include_router(
        transit_details_router, prefix="/api/transit-details", tags=["TransitDetails"]
    )
