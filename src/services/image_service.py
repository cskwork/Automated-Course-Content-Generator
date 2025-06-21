"""
Unsplash API 이미지 서비스
"""
import re
from typing import List, Optional
import requests
import streamlit as st

from src.config.settings import settings
from src.models.content_types import ImageInfo


class ImageService:
    """이미지 검색 및 처리 서비스"""
    
    def __init__(self):
        self.api_key = settings.UNSPLASH_API_KEY
        self.base_url = "https://api.unsplash.com/search/photos"
    
    def search_images(self, query: str, per_page: int = 5) -> List[ImageInfo]:
        """Unsplash API를 사용하여 이미지 검색"""
        if not self.api_key:
            st.warning("UNSPLASH_API_KEY가 설정되지 않았습니다. 이미지가 표시되지 않습니다.")
            return []
        
        headers = {"Authorization": f"Client-ID {self.api_key}"}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            images = []
            for photo in data.get("results", []):
                images.append(ImageInfo(
                    id=photo["id"],
                    url=photo["urls"]["regular"],
                    thumb_url=photo["urls"]["small"],
                    description=photo.get("description", photo.get("alt_description", "")),
                    author=photo["user"]["name"],
                    author_url=photo["user"]["links"]["html"]
                ))
            
            return images
            
        except requests.exceptions.RequestException as e:
            st.error(f"Unsplash API 오류: {str(e)}")
            return []
    
    def get_image_for_topic(self, topic: str, subject: str = "educational") -> Optional[ImageInfo]:
        """주제에 맞는 교육용 이미지 가져오기"""
        # 교육용 키워드 추가
        base_keyword = settings.EDUCATIONAL_KEYWORDS.get(subject, "education learning")
        search_query = f"{topic} {base_keyword}"
        
        # 이미지 검색
        images = self.search_images(search_query, per_page=1)
        
        if images:
            return images[0]
        else:
            # 대체 검색어로 재시도
            images = self.search_images(base_keyword, per_page=1)
            return images[0] if images else None
    
    def extract_placeholders(self, content: str) -> List[str]:
        """컨텐츠에서 이미지 플레이스홀더 추출"""
        pattern = r'\[이미지: ([^\]]+)\]'
        return re.findall(pattern, content)
    
    def replace_placeholders(self, content: str, subject: str) -> str:
        """이미지 플레이스홀더를 실제 이미지로 교체"""
        placeholders = self.extract_placeholders(content)
        
        for placeholder in placeholders:
            image_info = self.get_image_for_topic(placeholder, subject)
            
            if image_info:
                image_html = image_info.to_html(placeholder)
                content = content.replace(f'[이미지: {placeholder}]', image_html)
            else:
                # 이미지를 찾을 수 없는 경우
                placeholder_html = f'<div class="image-placeholder">이미지: {placeholder}</div>'
                content = content.replace(f'[이미지: {placeholder}]', placeholder_html)
        
        return content
    
    def enhance_content_with_images(self, content: str, subject: str) -> str:
        """컨텐츠에 이미지 추가"""
        if not self.api_key:
            return content
        
        with st.spinner("관련 이미지를 검색중입니다... 🖼️"):
            return self.replace_placeholders(content, subject)


# 싱글톤 인스턴스
image_service = ImageService() 