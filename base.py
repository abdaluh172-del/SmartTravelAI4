"""
Flight Provider Base Interface
================================
كل مزود بيانات رحلات (حقيقي أو تجريبي) يجب أن يرث من هذه الفئة
ويطبّق دالة search(). هذا يسمح بإضافة شركات طيران أو مصادر بيانات
جديدة لاحقًا دون الحاجة لإعادة بناء المشروع - فقط أضف Adapter جديد
وسجّله في providers/registry.py
"""
from abc import ABC, abstractmethod


class FlightProvider(ABC):
    #: مفتاح فريد يعرّف هذا المزود (مثال: "mock", "amadeus", "flysaudia")
    key = "base"
    #: هل هذا المزود يعيد بيانات حقيقية أم تجريبية
    is_mock = True

    @abstractmethod
    def search(self, origin, destination, depart_date, return_date=None,
               passengers=1, cabin_class="economy"):
        """
        يجب أن تعيد قائمة من القواميس (dict) بالشكل التالي لكل رحلة:

        {
            "id": str,
            "provider": str,
            "airline_code": str,
            "airline_name": str,
            "airline_name_ar": str,
            "logo_url": str | None,
            "origin": str,
            "destination": str,
            "depart_time": ISO datetime string,
            "arrive_time": ISO datetime string,
            "duration_minutes": int,
            "stops": int,
            "price": float,
            "currency": str,
            "cabin_class": str,
            "booking_url": str | None,
            "is_mock": bool
        }
        """
        raise NotImplementedError
