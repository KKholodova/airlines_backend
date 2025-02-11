import segno
import base64
from io import BytesIO
from datetime import datetime
from app.models import Flight

def generate_flight_qr(flight):
    """Генерирует QR-код для авиарейса"""
    status_dict = dict(Flight.STATUS_CHOICES)

    # Формируем текст для QR-кода
    info = (
        f"Авиарейс №{flight.pk}\n"
        f"Создатель: {flight.owner.username}\n"
        f"Статус: {status_dict.get(flight.status, 'Неизвестен')}\n"
    )

    # Добавляем сведения о рейсе
    info += f"\nИз аэропорта: {flight.from_airport}\n"
    info += f"В аэропорт: {flight.to_airport}\n"
    info += f"Код рейса: {flight.code}\n"
    info += f"Дата рейса: {flight.date.strftime('%Y-%m-%d %H:%M:%S')}\n"

    # Добавляем дополнительную информацию
    info += (
        f"\nДата создания: {flight.date_created.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    if flight.date_complete:
        info += f"Дата завершения: {flight.date_complete.strftime('%Y-%m-%d %H:%M:%S')}\n"

    print(info)
    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    print(qr_image_base64)

    return qr_image_base64