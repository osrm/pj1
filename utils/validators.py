"""
데이터 검증 유틸리티
"""
from typing import Optional


class DataValidator:
    """데이터 검증 클래스"""

    @staticmethod
    def validate_percentage(value: Optional[float]) -> bool:
        """
        퍼센트 값 검증 (0~100)

        Args:
            value: 퍼센트 값

        Returns:
            유효 여부
        """
        if value is None:
            return True
        return 0 <= value <= 100

    @staticmethod
    def validate_price(value: Optional[float]) -> bool:
        """
        가격 검증 (양수)

        Args:
            value: 가격

        Returns:
            유효 여부
        """
        if value is None:
            return True
        return value > 0

    @staticmethod
    def validate_name(name: Optional[str]) -> bool:
        """
        이름 검증 (비어있지 않음)

        Args:
            name: 이름

        Returns:
            유효 여부
        """
        if not name:
            return False
        return len(name.strip()) > 0

    @staticmethod
    def validate_calories(value: Optional[float]) -> bool:
        """
        칼로리 검증 (양수)

        Args:
            value: 칼로리

        Returns:
            유효 여부
        """
        if value is None:
            return True
        return value > 0
