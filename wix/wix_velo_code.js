/**
 * Wix Velo Code for "레벨 테스트 시작" Button
 *
 * 설치 방법:
 * 1. Wix Editor → 개발 모드 활성화
 * 2. "레벨 테스트 시작" 버튼 선택
 * 3. 버튼 ID를 "btnStartTest"로 변경
 * 4. 페이지 코드에 아래 내용 추가
 */

import wixUsers from 'wix-users';
import { fetch } from 'wix-fetch';

// ✅ 배포된 Backend URL
const BACKEND_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';

$w.onReady(function () {
    console.log('Wix 페이지 준비 완료');

    // "레벨 테스트 시작" 버튼 클릭 이벤트
    $w('#btnStartTest').onClick(async () => {
        console.log('레벨 테스트 시작 버튼 클릭됨');

        try {
            // 1. 로그인 상태 확인
            const isLoggedIn = wixUsers.currentUser.loggedIn;

            if (!isLoggedIn) {
                // 게스트 사용자 → 게스트 체험 페이지로 이동
                console.log('게스트 사용자 - 게스트 체험 페이지로 이동');
                wixLocation.to(`${BACKEND_URL}?mode=guest`);
                return;
            }

            // 2. 회원 정보 가져오기
            const user = wixUsers.currentUser;
            const wixUserId = user.id;
            const email = await user.getEmail();

            console.log(`회원 로그인 - Wix User ID: ${wixUserId}, Email: ${email}`);

            // 3. Firebase Custom Token 요청
            const response = await fetch(`${BACKEND_URL}/wix_login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wix_user_id: wixUserId,
                    email: email
                })
            });

            if (!response.ok) {
                throw new Error(`API 오류: ${response.status}`);
            }

            const data = await response.json();
            const customToken = data.custom_token;
            const firebaseUid = data.firebase_uid;

            console.log(`Firebase Custom Token 발급 성공 - UID: ${firebaseUid}`);

            // 4. Custom Token을 URL 파라미터로 전달하여 앱으로 이동
            wixLocation.to(`${BACKEND_URL}?token=${customToken}&uid=${firebaseUid}`);

        } catch (error) {
            console.error('레벨 테스트 시작 실패:', error);

            // 에러 알림 표시
            $w('#textErrorMessage').text = '로그인 중 오류가 발생했습니다. 다시 시도해주세요.';
            $w('#textErrorMessage').show();

            // 3초 후 에러 메시지 숨김
            setTimeout(() => {
                $w('#textErrorMessage').hide();
            }, 3000);
        }
    });
});
