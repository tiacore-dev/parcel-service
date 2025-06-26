from fastapi import FastAPI
from tiacore_lib.routes.auth_route import auth_router
from tiacore_lib.routes.company_route import company_router
from tiacore_lib.routes.invite_route import invite_router
from tiacore_lib.routes.register_route import register_router
from tiacore_lib.routes.role_route import role_router
from tiacore_lib.routes.user_route import user_router

from .parcel_cargo_route import parcel_cargo_router
from .parcel_product_route import parcel_product_router
from .parcel_route import parcel_router


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
