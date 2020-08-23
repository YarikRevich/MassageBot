
class TypeValidator:

    @staticmethod
    async def is_digit(value) -> bool:
        """Checks whether value is int or float"""

        try:
            float(value) or int(value)
            return True
        except ValueError as e:
            return False