#!/usr/bin/env python3
"""
Jira API 클라이언트 테스트 스크립트
실제 Jira에 테스트 티켓을 생성합니다.
"""
import sys
import json
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from lib.jira_client import JiraClient


def load_config():
    """설정 파일 로드"""
    config_path = Path(__file__).parent / "config" / "workflow_config.json"

    if not config_path.exists():
        print("❌ config/workflow_config.json 파일이 없습니다.")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_connection(jira: JiraClient):
    """연결 테스트"""
    print("=" * 60)
    print("Test 1: Jira 연결 테스트")
    print("=" * 60)

    project = jira.get_project_info()
    if project:
        print(f"✅ 프로젝트 연결 성공!")
        print(f"   이름: {project.get('name')}")
        print(f"   키: {project.get('key')}")
        print(f"   URL: {jira.base_url}/browse/{project.get('key')}")
        return True
    else:
        print("❌ 프로젝트 연결 실패")
        return False


def test_create_issue(jira: JiraClient):
    """이슈 생성 테스트"""
    print("\n" + "=" * 60)
    print("Test 2: 이슈 생성 테스트")
    print("=" * 60)

    result = jira.create_issue(
        summary="[테스트] Workflow 자동화 시스템 테스트",
        description="Jira API 클라이언트 테스트를 위한 이슈입니다. 자동으로 생성되었습니다.",
        issue_type="Task",
        labels=["automation", "test"]
    )

    if result['success']:
        print(f"✅ 이슈 생성 성공!")
        print(f"   키: {result['key']}")
        print(f"   URL: {result['url']}")
        return result['key']
    else:
        print("❌ 이슈 생성 실패")
        return None


def test_create_subtasks(jira: JiraClient, parent_key: str):
    """서브태스크 생성 테스트"""
    print("\n" + "=" * 60)
    print("Test 3: 서브태스크 생성 테스트")
    print("=" * 60)

    subtasks = [
        {
            "summary": "[자동] 백엔드 API 개발",
            "description": "자동화된 백엔드 개발 태스크",
            "labels": ["automation", "backend"]
        },
        {
            "summary": "[수동] UI/UX 디자인 검토",
            "description": "사용자가 직접 수행할 디자인 검토",
            "labels": ["manual", "frontend"]
        },
        {
            "summary": "[자동] 배포 및 테스트",
            "description": "자동화된 배포 프로세스",
            "labels": ["automation", "deployment"]
        }
    ]

    created_subtasks = []
    for subtask in subtasks:
        result = jira.create_subtask(
            parent_key=parent_key,
            **subtask
        )

        if result['success']:
            print(f"✅ 서브태스크 생성: {result['key']}")
            created_subtasks.append(result['key'])
        else:
            print(f"❌ 서브태스크 생성 실패")

    return created_subtasks


def test_add_comment(jira: JiraClient, issue_key: str):
    """댓글 추가 테스트"""
    print("\n" + "=" * 60)
    print("Test 4: 댓글 추가 테스트")
    print("=" * 60)

    success = jira.add_comment(
        issue_key,
        "🤖 Workflow 자동화 시스템에서 생성된 댓글입니다.\n\n테스트가 완료되었습니다!"
    )

    if success:
        print(f"✅ 댓글 추가 성공")
    else:
        print(f"❌ 댓글 추가 실패")

    return success


def test_get_issue(jira: JiraClient, issue_key: str):
    """이슈 조회 테스트"""
    print("\n" + "=" * 60)
    print("Test 5: 이슈 조회 테스트")
    print("=" * 60)

    issue = jira.get_issue(issue_key)

    if issue:
        print(f"✅ 이슈 조회 성공")
        print(f"   제목: {issue['fields']['summary']}")
        print(f"   상태: {issue['fields']['status']['name']}")
        print(f"   생성일: {issue['fields']['created']}")
        assignee = issue['fields'].get('assignee')
        assignee_name = assignee.get('displayName', '없음') if assignee else '없음'
        print(f"   담당자: {assignee_name}")
        return True
    else:
        print(f"❌ 이슈 조회 실패")
        return False


def main():
    """메인 함수"""
    print("🚀 Jira API 클라이언트 테스트 시작\n")

    # 설정 로드
    config = load_config()
    jira = JiraClient(config['jira'])

    # Test 1: 연결 테스트
    if not test_connection(jira):
        print("\n❌ 연결 테스트 실패. 종료합니다.")
        return

    # Test 2: 이슈 생성
    parent_key = test_create_issue(jira)
    if not parent_key:
        print("\n❌ 이슈 생성 실패. 종료합니다.")
        return

    # Test 3: 서브태스크 생성
    subtask_keys = test_create_subtasks(jira, parent_key)

    # Test 4: 댓글 추가
    test_add_comment(jira, parent_key)

    # Test 5: 이슈 조회
    test_get_issue(jira, parent_key)

    # 최종 결과
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)
    print(f"\n📋 생성된 이슈: {jira.base_url}/browse/{parent_key}")
    print(f"   - 부모 이슈: {parent_key}")
    print(f"   - 서브태스크: {len(subtask_keys)}개")
    print("\n💡 다음 단계:")
    print("   1. Jira 웹에서 생성된 이슈 확인")
    print("   2. 수동으로 댓글 '승인' 추가 테스트")
    print("   3. 상태 변경 테스트")
    print("\n⚠️  이 이슈는 테스트용이므로 나중에 삭제하셔도 됩니다.")


if __name__ == "__main__":
    main()
