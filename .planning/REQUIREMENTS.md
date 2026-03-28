# Requirements: Speechmate v1.2

**Defined:** 2026-03-28
**Core Value:** Пользователь загружает аудио и получает структурированный анализ содержания через LLM

## v1.2 Requirements

### Nginx

- [x] **NGX-01**: Nginx контейнер как единая точка входа на порту 80
- [x] **NGX-02**: Маршрутизация `/api/ingress/` → data_ingress, `/api/analysis/` → llm_analysis, `/` → frontend
- [x] **NGX-03**: proxy_read_timeout 300s для эндпоинта загрузки аудио
- [x] **NGX-04**: WebSocket upgrade headers для Vite HMR в dev-режиме
- [x] **NGX-05**: Удаление Vite proxy из vite.config.ts

### Authentication

- [x] **AUTH-01**: Пользователь может зарегистрироваться по email и паролю
- [x] **AUTH-02**: Пользователь может войти и получить JWT access token
- [x] **AUTH-03**: Все /recordings/* эндпоинты требуют JWT (кроме internal status callback)
- [x] **AUTH-04**: Все /analysis/* эндпоинты требуют JWT
- [x] **AUTH-05**: Список записей фильтруется по user_id из JWT
- [x] **AUTH-06**: Загрузка записи привязывает user_id из JWT (не из query param)
- [x] **AUTH-07**: Фронтенд: страница логина и регистрации
- [x] **AUTH-08**: Фронтенд: axios interceptor для Authorization header
- [x] **AUTH-09**: Фронтенд: редирект неавторизованных на /login

### UX Redesign

- [x] **UX-01**: Workspace — главная страница (/ → WorkspacePage)
- [x] **UX-02**: Кнопка "+" в сайдбаре открывает модал загрузки файла
- [x] **UX-03**: Пустое состояние workspace с подсказкой "Добавьте первую запись"
- [x] **UX-04**: Чат-пузыри: сообщения пользователя справа, AI слева, с рамками и фоном
- [x] **UX-05**: Переливающаяся shimmer-анимация на названии записи при обработке
- [x] **UX-06**: Прогресс-бар этапов при наведении на запись в сайдбаре

### Testing

- [ ] **TEST-01**: Unit тесты RecordingService (upload, get_page, status transitions)
- [ ] **TEST-02**: Unit тесты UnitOfWork (commit/rollback координация)
- [ ] **TEST-03**: Unit тесты RecordingRepository (add, get_by_id, update_status, get_page)
- [ ] **TEST-04**: Unit тесты AuthService (register, login, verify_token)

## Future Requirements

- Refresh token с автоматическим обновлением
- OAuth (Google, Яндекс)
- SSL/HTTPS в nginx
- User profile management
- E2E / integration tests

## Out of Scope

| Feature | Reason |
|---------|--------|
| OAuth login | Extra complexity; basic JWT sufficient for v1.2 |
| SSL/HTTPS | Dev environment only; add for production |
| Token blacklist | Short-lived tokens + client-side deletion sufficient |
| Role-based access control | Over-engineering for current scale |
| Tests for transcription/dialogue_detection | ML-heavy, hard to unit-test |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| NGX-01 | Phase 9 | Complete |
| NGX-02 | Phase 9 | Complete |
| NGX-03 | Phase 9 | Complete |
| NGX-04 | Phase 9 | Complete |
| NGX-05 | Phase 9 | Complete |
| AUTH-01 | Phase 10 | Complete |
| AUTH-02 | Phase 10 | Complete |
| AUTH-03 | Phase 10 | Complete |
| AUTH-04 | Phase 10 | Complete |
| AUTH-05 | Phase 10 | Complete |
| AUTH-06 | Phase 10 | Complete |
| AUTH-07 | Phase 10 | Complete |
| AUTH-08 | Phase 10 | Complete |
| AUTH-09 | Phase 10 | Complete |
| UX-01 | Phase 11 | Complete |
| UX-02 | Phase 11 | Complete |
| UX-03 | Phase 11 | Complete |
| UX-04 | Phase 11 | Complete |
| UX-05 | Phase 11 | Complete |
| UX-06 | Phase 11 | Complete |
| TEST-01 | Phase 12 | Pending |
| TEST-02 | Phase 12 | Pending |
| TEST-03 | Phase 12 | Pending |
| TEST-04 | Phase 12 | Pending |

**Coverage:**
- v1.2 requirements: 24 total
- Mapped to phases: 24
- Unmapped: 0

---
*Requirements defined: 2026-03-28*
*Traceability updated: 2026-03-28*
