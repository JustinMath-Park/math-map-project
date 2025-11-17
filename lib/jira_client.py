#!/usr/bin/env python3
"""
Jira API 클라이언트
티켓 생성, 서브태스크 관리, 상태 변경, 승인 대기 등
"""
import requests
import time
import json
from typing import Dict, List, Optional
from datetime import datetime


class JiraClient:
    """Jira API 래퍼 클래스"""

    def __init__(self, config: Dict):
        """
        Jira 클라이언트 초기화

        Args:
            config: Jira 설정 딕셔너리
                - base_url: Jira 인스턴스 URL
                - email: 사용자 이메일
                - api_token: API 토큰
                - project_key: 프로젝트 키 (예: KAN)
        """
        self.base_url = config['base_url'].rstrip('/')
        self.email = config['email']
        self.api_token = config['api_token']
        self.project_key = config['project_key']
        self.auth = (self.email, self.api_token)

    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Jira 이슈 생성

        Args:
            summary: 이슈 제목
            description: 이슈 설명
            issue_type: 이슈 타입 (Task, Story, Bug 등)
            labels: 라벨 리스트

        Returns:
            생성된 이슈 정보 (key, id, url 포함)
        """
        url = f"{self.base_url}/rest/api/3/issue"

        # 설명을 Atlassian Document Format (ADF)로 변환
        adf_description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": description}
                    ]
                }
            ]
        }

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": adf_description,
                "issuetype": {"name": issue_type}
            }
        }

        # 라벨 추가
        if labels:
            payload["fields"]["labels"] = labels

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            issue_key = result['key']
            issue_id = result['id']

            return {
                'key': issue_key,
                'id': issue_id,
                'url': f"{self.base_url}/browse/{issue_key}",
                'success': True
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Jira 이슈 생성 실패: {e}")
            if hasattr(e.response, 'text'):
                print(f"   상세: {e.response.text}")
            return {'success': False, 'error': str(e)}

    def create_subtask(
        self,
        parent_key: str,
        summary: str,
        description: str,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        서브태스크 생성

        Args:
            parent_key: 부모 이슈 키 (예: KAN-123)
            summary: 서브태스크 제목
            description: 서브태스크 설명
            labels: 라벨 리스트

        Returns:
            생성된 서브태스크 정보
        """
        url = f"{self.base_url}/rest/api/3/issue"

        adf_description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": description}
                    ]
                }
            ]
        }

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "parent": {"key": parent_key},
                "summary": summary,
                "description": adf_description,
                "issuetype": {"name": "Subtask"}
            }
        }

        if labels:
            payload["fields"]["labels"] = labels

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            return {
                'key': result['key'],
                'id': result['id'],
                'url': f"{self.base_url}/browse/{result['key']}",
                'success': True
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ 서브태스크 생성 실패: {e}")
            if hasattr(e.response, 'text'):
                print(f"   상세: {e.response.text}")
            return {'success': False, 'error': str(e)}

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """
        이슈 정보 조회

        Args:
            issue_key: 이슈 키 (예: KAN-123)

        Returns:
            이슈 정보 딕셔너리
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ 이슈 조회 실패: {e}")
            return None

    def update_status(self, issue_key: str, status: str) -> bool:
        """
        이슈 상태 변경

        Args:
            issue_key: 이슈 키
            status: 변경할 상태 (To Do, In Progress, Done 등)

        Returns:
            성공 여부
        """
        # 1. 사용 가능한 transition 조회
        transitions_url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"

        try:
            response = requests.get(transitions_url, auth=self.auth)
            response.raise_for_status()
            transitions = response.json()['transitions']

            # 원하는 상태의 transition ID 찾기
            transition_id = None
            for t in transitions:
                if t['name'].lower() == status.lower() or t['to']['name'].lower() == status.lower():
                    transition_id = t['id']
                    break

            if not transition_id:
                print(f"⚠️  '{status}' 상태로 변경할 수 없습니다.")
                print(f"   사용 가능한 상태: {[t['to']['name'] for t in transitions]}")
                return False

            # 2. Transition 실행
            payload = {
                "transition": {"id": transition_id}
            }

            response = requests.post(
                transitions_url,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            print(f"✅ {issue_key} 상태 변경: {status}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 상태 변경 실패: {e}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        이슈에 댓글 추가

        Args:
            issue_key: 이슈 키
            comment: 댓글 내용

        Returns:
            성공 여부
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"

        adf_comment = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": comment}
                    ]
                }
            ]
        }

        payload = {"body": adf_comment}

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"✅ 댓글 추가: {issue_key}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 댓글 추가 실패: {e}")
            return False

    def wait_for_approval(
        self,
        issue_key: str,
        approval_keyword: str = "승인",
        check_interval: int = 30,
        timeout: int = 3600
    ) -> bool:
        """
        이슈 승인 대기 (댓글 또는 상태 변경 감지)

        Args:
            issue_key: 이슈 키
            approval_keyword: 승인 키워드 (댓글에서 찾을 단어)
            check_interval: 체크 간격 (초)
            timeout: 타임아웃 (초)

        Returns:
            승인 여부
        """
        print(f"⏳ {issue_key} 승인 대기 중...")
        print(f"   Jira에서 '{approval_keyword}' 댓글을 입력하거나")
        print(f"   상태를 'In Progress'로 변경하세요.")

        start_time = time.time()
        last_comment_count = 0

        while time.time() - start_time < timeout:
            # 이슈 정보 조회
            issue = self.get_issue(issue_key)
            if not issue:
                time.sleep(check_interval)
                continue

            # 1. 상태 확인
            status = issue['fields']['status']['name']
            if status.lower() in ['in progress', 'done']:
                print(f"✅ 상태 변경 감지: {status}")
                return True

            # 2. 댓글 확인
            comments = issue['fields'].get('comment', {}).get('comments', [])
            if len(comments) > last_comment_count:
                # 새 댓글이 있음
                new_comments = comments[last_comment_count:]
                for comment in new_comments:
                    body_text = self._extract_text_from_adf(comment['body'])
                    if approval_keyword in body_text:
                        print(f"✅ 승인 댓글 발견: {body_text[:50]}")
                        return True
                last_comment_count = len(comments)

            # 대기
            print(f"   ⏰ {int(time.time() - start_time)}초 경과...")
            time.sleep(check_interval)

        print(f"⏱️  타임아웃: 승인되지 않음")
        return False

    def _extract_text_from_adf(self, adf: Dict) -> str:
        """
        Atlassian Document Format에서 텍스트 추출

        Args:
            adf: ADF 딕셔너리

        Returns:
            추출된 텍스트
        """
        if not adf or 'content' not in adf:
            return ""

        text_parts = []
        for content_block in adf['content']:
            if content_block.get('type') == 'paragraph':
                for item in content_block.get('content', []):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))

        return ' '.join(text_parts)

    def get_project_info(self) -> Optional[Dict]:
        """
        프로젝트 정보 조회 (연결 테스트용)

        Returns:
            프로젝트 정보
        """
        url = f"{self.base_url}/rest/api/3/project/{self.project_key}"

        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ 프로젝트 조회 실패: {e}")
            return None
