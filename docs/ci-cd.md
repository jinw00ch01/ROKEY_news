# CI/CD 설계

## 브랜치 전략
- `main`: 배포 브랜치. PR 머지 시 자동 배포.
- `feature/*`: 작업 브랜치, PR에서 테스트/빌드만 수행.

## GitHub Actions 워크플로 초안
1) **ci-frontend.yml**
   - 트리거: PR/푸시(main, feature).
   - Job: `npm ci` → `npm run lint` → `npm run build`.
   - 아티팩트: `frontend/dist`.
2) **ci-backend.yml**
   - 트리거: PR/푸시(main, feature).
   - Job: `pip install -r backend/requirements.txt` → 유닛/서비스 테스트(pytest) → mypy(optional).
3) **deploy-frontend.yml**
   - 트리거: main push 성공 시.
   - 대상: Vercel 혹은 GitHub Pages. (Vercel 선호)
   - 입력: `VERCEL_TOKEN`, `VERCEL_PROJECT_ID`, `VERCEL_ORG_ID` 시크릿.
4) **deploy-backend.yml**
   - 트리거: main push 성공 시.
   - 대상: Render/Cloud Run 중 Render 가벼운 선택.
   - 입력(Render): `RENDER_SERVICE_ID`, `RENDER_API_KEY`.

## 시크릿/환경 변수
- 공통: `GEMINI_API_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS`, `RATE_LIMIT_PER_MIN`.
- 프런트 빌드: 백엔드 API URL(`VITE_API_BASE_URL`).
- GitHub: `ACTIONS_STEP_DEBUG`는 필요 시만.

## 배포 전략
- 프런트: Vercel에 `frontend` 루트로 빌드(`npm run build`), 프레임워크 설정 자동.
- 백엔드: Render Web Service, start `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
- 헬스체크: `/health` 200.

## 롤백/모니터링
- Vercel: 이전 배포로 롤백 버튼.
- Render: 이전 버전 재배포.
- 알림: 워크플로 실패 시 Slack/Webhook(추후 추가).

## 로컬/도구
- `.env.example`로 필수 키 공유.
- pre-commit 훅(선택): black/ruff/mypy, eslint/prettier.

