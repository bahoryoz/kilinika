from rest_framework.exceptions import APIException


class SlotConflictError(APIException):
    status_code = 409
    default_detail = 'Bu vaqt endigina band qilindi'
    default_code = 'slot_conflict'
