"""
로깅 시스템 - 컨텐츠 생성 진행상황 추적
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class ContentLogger:
    """컨텐츠 생성 로깅 클래스"""
    
    def __init__(self):
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """로거 설정"""
        # logs 디렉토리 생성
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # 로거 생성
        self.logger = logging.getLogger("content_generator")
        self.logger.setLevel(logging.INFO)
        
        # 핸들러가 이미 있으면 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 파일 핸들러 설정
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"content_generation_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_start(self, config_info: str):
        """컨텐츠 생성 시작 로그"""
        self.logger.info(f"=== 컨텐츠 생성 시작 ===")
        self.logger.info(f"설정: {config_info}")
    
    def log_step(self, step: str, details: str = ""):
        """컨텐츠 생성 단계 로그"""
        message = f"단계: {step}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_completion(self, step: str, token_count: int = None):
        """단계 완료 로그"""
        message = f"완료: {step}"
        if token_count:
            message += f" (토큰: {token_count})"
        self.logger.info(message)
    
    def log_error(self, step: str, error: str):
        """에러 로그"""
        self.logger.error(f"오류 [{step}]: {error}")
    
    def log_finish(self, total_time: float = None):
        """컨텐츠 생성 완료 로그"""
        message = "=== 컨텐츠 생성 완료 ==="
        if total_time:
            message += f" (총 시간: {total_time:.2f}초)"
        self.logger.info(message)


# 싱글톤 인스턴스
content_logger = ContentLogger()