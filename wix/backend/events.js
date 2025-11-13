/**
 * Wix Velo Backend Events
 *
 * 설치 방법:
 * 1. Wix Editor → Dev Mode 활성화
 * 2. 좌측 패널 → Backend 섹션 → "events.js" 파일 생성
 * 3. 아래 코드 복사/붙여넣기
 * 4. Publish
 */

import { fetch } from 'wix-fetch';
import wixSecretsBackend from 'wix-secrets-backend';

// Backend API URL
const BACKEND_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';

/**
 * 회원 생성 이벤트
 */
export function wixUsers_onLogin(event) {
    console.log('회원 로그인 이벤트:', event);

    const userId = event.user.id;
    const email = event.user.loginEmail;

    // Firebase에 동기화
    syncUserToFirebase(userId, email, 'login');
}

/**
 * 회원 가입 이벤트
 */
export function wixUsers_onRegister(event) {
    console.log('회원 가입 이벤트:', event);

    const userId = event.user.id;
    const email = event.user.loginEmail;

    // Firebase에 동기화
    syncUserToFirebase(userId, email, 'created');
}

/**
 * 회원 정보 업데이트 이벤트
 */
export function wixUsers_onUserUpdate(event) {
    console.log('회원 정보 업데이트 이벤트:', event);

    const userId = event.user.id;
    const email = event.user.loginEmail;

    // Firebase에 동기화
    syncUserToFirebase(userId, email, 'updated');
}

/**
 * Firebase 동기화 함수
 */
async function syncUserToFirebase(wixUserId, email, eventType) {
    try {
        const response = await fetch(`${BACKEND_URL}/wix_velo_sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wix_user_id: wixUserId,
                email: email,
                event_type: eventType
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Firebase 동기화 성공:', data);
            return data;
        } else {
            const errorText = await response.text();
            console.error('Firebase 동기화 실패:', response.status, errorText);
            return null;
        }
    } catch (error) {
        console.error('Firebase 동기화 에러:', error);
        return null;
    }
}
