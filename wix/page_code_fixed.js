/**
 * Wix 페이지 코드 - 개선된 버전
 *
 * 설치 방법:
 * 1. "레벨 테스트 시작" 버튼의 ID를 "btnStartTest"로 설정
 * 2. 페이지 코드에 아래 내용 복사/붙여넣기
 */

import wixUsers from 'wix-users';
import wixLocation from 'wix-location';
import { fetch } from 'wix-fetch';

const BACKEND_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';

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
                    mode: 'signup'  // 'signup' = 회원가입 모드, 'login' = 로그인 모드
                });

                console.log('✅ 회원가입/로그인 완료');
                // promptLogin이 성공하면 이미 로그인된 상태이므로 아래 로직 계속 진행
            }

            // 회원 정보 가져오기
            const user = wixUsers.currentUser;
            const wixUserId = user.id;
            const email = await user.getEmail();

            console.log(`👤 회원 로그인`);
            console.log(`   - Wix User ID: ${wixUserId}`);
            console.log(`   - Email: ${email}`);

            // 1. Firebase 동기화
            console.log('📤 Firebase 동기화 시작...');
            try {
                const syncResponse = await fetch(`${BACKEND_URL}/wix_velo_sync`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        wix_user_id: wixUserId,
                        email: email,
                        event_type: 'login'
                    })
                });

                console.log(`   - 동기화 응답 상태: ${syncResponse.status}`);

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

            // 2. Custom Token 발급
            console.log('🔑 Custom Token 요청 중...');
            const tokenResponse = await fetch(`${BACKEND_URL}/wix_login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    wix_user_id: wixUserId,
                    email: email
                })
            });

            console.log(`   - Token 응답 상태: ${tokenResponse.status}`);

            if (!tokenResponse.ok) {
                const errorText = await tokenResponse.text();
                console.error('❌ Custom Token 발급 실패:', tokenResponse.status, errorText);
                throw new Error(`Custom Token 발급 실패: ${tokenResponse.status}`);
            }

            const tokenData = await tokenResponse.json();
            console.log('   - Token 응답 데이터:', tokenData);

            const customToken = tokenData.custom_token;
            const firebaseUid = tokenData.firebase_uid;

            if (!customToken) {
                console.error('❌ Custom Token이 없습니다!', tokenData);
                throw new Error('Custom Token을 받지 못했습니다.');
            }

            console.log(`✅ Custom Token 발급 성공`);
            console.log(`   - Firebase UID: ${firebaseUid}`);
            console.log(`   - Token (앞 30자): ${customToken.substring(0, 30)}...`);

            // 3. 레벨 테스트 앱으로 이동 (토큰을 URL 해시로 전달)
            const FRONTEND_URL = 'https://my-mvp-backend.web.app';
            const appUrl = `${FRONTEND_URL}/test.html?token=${encodeURIComponent(customToken)}&uid=${encodeURIComponent(firebaseUid)}`;
            console.log('🚀 레벨 테스트 앱으로 이동 중...');

            wixLocation.to(appUrl);

        } catch (error) {
            console.error('⚠️ 오류 발생:', error);
            console.error('   - 에러 메시지:', error.message);
            console.error('   - 스택:', error.stack);

            // 사용자가 회원가입/로그인을 취소한 경우
            if (error.message && (error.message.includes('canceled') || error.message.includes('closed'))) {
                console.log('👤 사용자가 회원가입/로그인을 취소했습니다.');
                return;
            }

            // 사용자에게 알림
            alert('로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
    });
});
