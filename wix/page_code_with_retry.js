/**
 * Wix 페이지 코드 - 네트워크 재시도 로직 포함
 *
 * 설치 방법:
 * 1. "레벨 테스트 시작" 버튼의 ID를 "btnStartTest"로 설정
 * 2. 페이지 코드에 아래 내용 복사/붙여넣기
 *
 * 개선 사항:
 * - 네트워크 에러 시 자동 재시도 (최대 3회)
 * - 명확한 에러 메시지 표시
 * - 타임아웃 설정
 */

import wixUsers from 'wix-users';
import wixLocation from 'wix-location';
import { fetch } from 'wix-fetch';

const BACKEND_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1초
const REQUEST_TIMEOUT = 30000; // 30초

/**
 * 지연 함수
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 타임아웃 기능이 있는 fetch
 */
async function fetchWithTimeout(url, options, timeout = REQUEST_TIMEOUT) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('NETWORK_TIMEOUT');
        }
        throw error;
    }
}

/**
 * 재시도 로직이 포함된 fetch
 */
async function fetchWithRetry(url, options, maxRetries = MAX_RETRIES) {
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`🔄 API 요청 시도 ${attempt}/${maxRetries}`);
            const response = await fetchWithTimeout(url, options);

            // 성공
            if (response.ok) {
                console.log(`✅ API 요청 성공 (시도 ${attempt}/${maxRetries})`);
                return response;
            }

            // 4xx 에러는 재시도하지 않음 (클라이언트 에러)
            if (response.status >= 400 && response.status < 500) {
                console.error(`❌ 클라이언트 에러: ${response.status}`);
                return response;
            }

            // 5xx 에러는 재시도
            console.warn(`⚠️ 서버 에러 (${response.status}), 재시도 중...`);
            lastError = new Error(`서버 에러: ${response.status}`);

        } catch (error) {
            console.error(`⚠️ 네트워크 에러 (시도 ${attempt}/${maxRetries}):`, error.message);
            lastError = error;

            // 타임아웃이나 네트워크 에러인 경우
            if (error.message === 'NETWORK_TIMEOUT') {
                lastError = new Error('NETWORK_TIMEOUT');
            } else {
                lastError = new Error('NETWORK_ERROR');
            }
        }

        // 마지막 시도가 아니면 재시도 전 대기
        if (attempt < maxRetries) {
            console.log(`⏳ ${RETRY_DELAY}ms 후 재시도...`);
            await delay(RETRY_DELAY * attempt); // 점진적 대기 (1초, 2초, 3초...)
        }
    }

    // 모든 재시도 실패
    throw lastError;
}

/**
 * 사용자에게 친화적인 에러 메시지 반환
 */
function getErrorMessage(error) {
    if (error.message === 'NETWORK_TIMEOUT') {
        return '네트워크 연결이 느립니다.\n안정적인 Wi-Fi 환경에서 다시 시도해주세요.';
    }

    if (error.message === 'NETWORK_ERROR') {
        return '네트워크 연결에 문제가 있습니다.\n인터넷 연결을 확인하고 다시 시도해주세요.';
    }

    if (error.message && error.message.includes('서버 에러')) {
        return '서버에 일시적인 문제가 발생했습니다.\n잠시 후 다시 시도해주세요.';
    }

    return '오류가 발생했습니다.\n다시 시도해주세요.';
}

$w.onReady(function () {
    console.log('✅ 페이지 준비 완료');

    $w('#btnStartTest').onClick(async () => {
        console.log('🔵 버튼 클릭됨');

        try {
            const isLoggedIn = wixUsers.currentUser.loggedIn;

            if (!isLoggedIn) {
                console.log('👤 비로그인 사용자 - 회원가입 모달 열기');

                // Wix 회원가입 모달 열기
                await wixUsers.promptLogin({
                    mode: 'signup'
                });

                console.log('✅ 회원가입/로그인 완료');
            }

            // 회원 정보 가져오기
            const user = wixUsers.currentUser;
            const wixUserId = user.id;
            const email = await user.getEmail();

            console.log(`👤 회원 로그인`);
            console.log(`   - Wix User ID: ${wixUserId}`);
            console.log(`   - Email: ${email}`);

            // 1. Firebase 동기화 (재시도 포함)
            console.log('📤 Firebase 동기화 시작...');
            try {
                const syncResponse = await fetchWithRetry(
                    `${BACKEND_URL}/wix_velo_sync`,
                    {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            wix_user_id: wixUserId,
                            email: email,
                            event_type: 'login'
                        })
                    }
                );

                if (syncResponse.ok) {
                    const syncData = await syncResponse.json();
                    console.log('✅ Firebase 동기화 성공:', syncData);
                } else {
                    const errorText = await syncResponse.text();
                    console.error('❌ Firebase 동기화 실패:', syncResponse.status, errorText);
                }
            } catch (syncError) {
                console.error('⚠️ Firebase 동기화 에러:', syncError);
                // 동기화 실패해도 계속 진행
            }

            // 2. Custom Token 발급 (재시도 포함)
            console.log('🔑 Custom Token 요청 중...');
            const tokenResponse = await fetchWithRetry(
                `${BACKEND_URL}/wix_login`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        wix_user_id: wixUserId,
                        email: email
                    })
                }
            );

            if (!tokenResponse.ok) {
                const errorText = await tokenResponse.text();
                console.error('❌ Custom Token 발급 실패:', tokenResponse.status, errorText);
                throw new Error(`Custom Token 발급 실패: ${tokenResponse.status}`);
            }

            const tokenData = await tokenResponse.json();
            const customToken = tokenData.custom_token;
            const firebaseUid = tokenData.firebase_uid;

            if (!customToken) {
                console.error('❌ Custom Token이 없습니다!', tokenData);
                throw new Error('Custom Token을 받지 못했습니다.');
            }

            console.log(`✅ Custom Token 발급 성공`);
            console.log(`   - Firebase UID: ${firebaseUid}`);

            // 3. 레벨 테스트 앱으로 이동
            const FRONTEND_URL = 'https://my-mvp-backend.web.app';
            const appUrl = `${FRONTEND_URL}/test.html?token=${encodeURIComponent(customToken)}&uid=${encodeURIComponent(firebaseUid)}`;
            console.log('🚀 레벨 테스트 앱으로 이동 중...');

            wixLocation.to(appUrl);

        } catch (error) {
            console.error('⚠️ 오류 발생:', error);
            console.error('   - 에러 메시지:', error.message);

            // 사용자가 회원가입/로그인을 취소한 경우
            if (error.message && (error.message.includes('canceled') || error.message.includes('closed'))) {
                console.log('👤 사용자가 회원가입/로그인을 취소했습니다.');
                return;
            }

            // 사용자에게 친화적인 에러 메시지 표시
            const userMessage = getErrorMessage(error);
            alert(userMessage);
        }
    });
});
