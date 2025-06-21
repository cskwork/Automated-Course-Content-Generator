"""
입력 검증 유틸리티
"""
from typing import Dict, List, Optional


class Validators:
    """입력값 검증 클래스"""
    
    @staticmethod
    def validate_course_config(config: Dict) -> tuple[bool, Optional[str]]:
        """교과서 설정 검증"""
        # 필수 필드 확인
        required_fields = ['unit_name', 'learning_objectives']
        for field in required_fields:
            if not config.get(field):
                return False, f"{field}를 입력해주세요."
        
        # 단원명 길이 확인
        if len(config.get('unit_name', '')) < 2:
            return False, "단원명은 최소 2자 이상이어야 합니다."
        
        # 학습 목표 길이 확인
        if len(config.get('learning_objectives', '')) < 10:
            return False, "학습 목표는 최소 10자 이상이어야 합니다."
        
        # 컨텐츠 유형 확인
        if not config.get('content_types'):
            return False, "최소 하나 이상의 컨텐츠 유형을 선택해주세요."
        
        return True, None
    
    @staticmethod
    def validate_api_key(provider: str, api_key: Optional[str]) -> bool:
        """API 키 검증"""
        if provider in ['openai', 'openrouter'] and not api_key:
            return False
        return True
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """입력값 정제"""
        # 공백 제거
        text = text.strip()
        # 특수문자 처리 (필요시 추가)
        return text
    
    @staticmethod
    def validate_export_format(format_type: str, valid_formats: List[str]) -> bool:
        """내보내기 형식 검증"""
        return format_type in valid_formats 