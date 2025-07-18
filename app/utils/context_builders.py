from app.database.models import Parcel, ParcelStatus


def flatten_context(obj, parent_key="", sep=".") -> dict:
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_context(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(flatten_context(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items


async def build_parcel_context(parcel: Parcel) -> dict:
    # Получаем связанные данные
    cargo_list = await parcel.parcel_cargo.all().prefetch_related("cargo_type")
    product_list = await parcel.parcel_products.all()
    last_status = await ParcelStatus.filter(parcel=parcel).order_by("-date").first()

    return {
        "parcel": {
            "parcel_id": str(parcel.id),
            "name": parcel.name,
            "note": parcel.note,
            "weight": float(parcel.weight),
            "volume": float(parcel.volume),
            "places_count": parcel.places_count,
            "pickup_estimated_date": parcel.pickup_estimated_date.strftime("%d.%m.%Y"),
            "pickup_time_from": str(parcel.pickup_time_from),
            "pickup_time_to": str(parcel.pickup_time_to),
            "delivery_estimated_date": parcel.delivery_estimated_date.strftime("%d.%m.%Y")
            if parcel.delivery_estimated_date
            else None,
            "delivery_time_from": str(parcel.delivery_time_from) if parcel.delivery_time_from else None,
            "delivery_time_to": str(parcel.delivery_time_to) if parcel.delivery_time_to else None,
            "sender": {
                "city": str(parcel.sender_city),
                "address": parcel.sender_address,
                "warehouse": str(parcel.sender_warehouse) if parcel.sender_warehouse else None,
                "delivery_type": parcel.sender_delivery_type.value,
                "personal_data": str(parcel.sender_personal_data) if parcel.sender_personal_data else None,
                "company": parcel.sender_company,
                "phone": parcel.sender_phone,
                "email": parcel.sender_email,
                "telegram": parcel.sender_telegram,
                "latitude": float(parcel.sender_coordinates_latitude) if parcel.sender_coordinates_latitude else None,
                "longitude": float(parcel.sender_coordinates_longitude)
                if parcel.sender_coordinates_longitude
                else None,
                "additional_info": parcel.sender_additional_info,
            },
            "recipient": {
                "city": str(parcel.recipient_city),
                "address": parcel.recipient_address,
                "warehouse": str(parcel.recipient_warehouse) if parcel.recipient_warehouse else None,
                "delivery_type": parcel.recipient_delivery_type.value,
                "personal_data": str(parcel.recipient_personal_data) if parcel.recipient_personal_data else None,
                "company": parcel.recipient_company,
                "phone": parcel.recipient_phone,
                "email": parcel.recipient_email,
                "telegram": parcel.recipient_telegram,
                "latitude": float(parcel.recipient_coordinates_latitude)
                if parcel.recipient_coordinates_latitude
                else None,
                "longitude": float(parcel.recipient_coordinates_longitude)
                if parcel.recipient_coordinates_longitude
                else None,
                "additional_info": parcel.recipient_additional_info,
            },
            "cargo": [
                {
                    "cargo_type": cargo.cargo_type.name if cargo.cargo_type else None,
                    "weight": float(cargo.weight),
                    "length": float(cargo.length),
                    "height": float(cargo.height),
                    "width": float(cargo.width),
                    "volume": float(cargo.volume),
                    "quantity": cargo.quantity,
                    "total_weight": float(cargo.total_weight),
                    "total_volume": float(cargo.total_volume),
                    "comment": cargo.comment,
                }
                for cargo in cargo_list
            ],
            "products": [
                {
                    "name": product.name,
                    "article_number": product.article_number,
                    "serial_number": product.serial_number,
                    "quantity": product.quantity,
                    "price": float(product.price),
                    "summ": float(product.summ),
                    "delivered": product.delivered,
                }
                for product in product_list
            ],
            "status": {
                "status": last_status.status.value if last_status else None,
                "date": last_status.date if last_status else None,
                "comment": last_status.comment if last_status else None,
            }
            if last_status
            else None,
        }
    }
