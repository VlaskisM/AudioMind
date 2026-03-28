# Roadmap: Speechmate

## Milestones

- ✅ **v1.0 LLM Analysis Service** - Phases 1-4 (shipped 2026-03-22)
- ✅ **v1.1 Web Frontend** - Phases 5-8 (shipped 2026-03-25)
- 🚧 **v1.2 Infrastructure & UX** - Phases 9-12 (in progress)

## Phases

<details>
<summary>✅ v1.0 LLM Analysis Service (Phases 1-4) — SHIPPED 2026-03-22</summary>

Phase 1: Foundation, Phase 2: Core Analysis, Phase 3: FAQ, Phase 4: Chat with Transcript
See v1.0-MILESTONE-AUDIT.md for details.

</details>

<details>
<summary>✅ v1.1 Web Frontend (Phases 5-8) — SHIPPED 2026-03-25</summary>

Phase 5: Backend API, Phase 6: Frontend Scaffold, Phase 7: Upload & Processing, Phase 8: Workspace
See v1.1-MILESTONE-AUDIT.md for details.

</details>

### 🚧 v1.2 Infrastructure & UX (In Progress)

- [x] **Phase 9: Nginx Reverse Proxy** - Единая точка входа на порту 80, маршрутизация ко всем сервисам (completed 2026-03-28)
- [x] **Phase 10: JWT Authentication** - Регистрация, вход, защита эндпоинтов, привязка данных к пользователю (completed 2026-03-28)
- [x] **Phase 11: UX Redesign** - Workspace как главная, загрузка через сайдбар, чат-пузыри, анимации (completed 2026-03-28)
- [ ] **Phase 12: Unit Tests** - Покрытие тестами data_ingress (сервисы, репозитории, UoW, auth)

## Phase Details

### Phase 9: Nginx Reverse Proxy
**Goal**: Все HTTP-запросы проходят через единую точку входа (nginx на порту 80), Vite proxy удалён
**Depends on**: Phase 8 (v1.1 shipped)
**Requirements**: NGX-01, NGX-02, NGX-03, NGX-04, NGX-05
**Success Criteria** (what must be TRUE):
  1. Пользователь открывает http://localhost и видит фронтенд приложения
  2. Фронтенд корректно загружает аудио через /api/ingress/ и получает анализы через /api/analysis/ — оба запроса идут на порт 80
  3. Загрузка больших аудиофайлов (до 5 минут обработки) не прерывается по таймауту
  4. Hot Module Replacement работает в dev-режиме (изменения в коде отражаются без перезагрузки)
  5. В vite.config.ts отсутствует секция proxy — весь трафик идёт через nginx
**Plans**: TBD

Plans:
- [ ] 09-01: Nginx config + Docker compose (NGX-01, NGX-02, NGX-03, NGX-04) [wave 1]
- [ ] 09-02: Удаление Vite proxy + CORS update (NGX-05) [wave 2, depends: 09-01]

### Phase 10: JWT Authentication
**Goal**: Пользователи могут регистрироваться, входить в систему и работать только со своими записями
**Depends on**: Phase 9
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, AUTH-07, AUTH-08, AUTH-09
**Success Criteria** (what must be TRUE):
  1. Новый пользователь может зарегистрироваться по email/паролю и сразу войти в систему
  2. Неавторизованный пользователь не может получить доступ к записям — все /recordings/* и /analysis/* возвращают 401
  3. Каждый пользователь видит только свои записи — загруженные файлы привязаны к user_id из токена
  4. Фронтенд автоматически подставляет токен в каждый запрос и перенаправляет на /login при отсутствии авторизации
  5. Внутренние worker-callback эндпоинты продолжают работать без JWT
**Plans**: 3 plans

Plans:
- [ ] 10-01-PLAN.md — Auth инфраструктура: User entity, AuthService, auth endpoints, get_current_user (AUTH-01, AUTH-02) [wave 1]
- [ ] 10-02-PLAN.md — Защита эндпоинтов: JWT на recordings + analysis, фильтрация по user_id (AUTH-03, AUTH-04, AUTH-05, AUTH-06) [wave 2, depends: 10-01]
- [ ] 10-03-PLAN.md — Фронтенд auth: login/register pages, interceptors, ProtectedRoute (AUTH-07, AUTH-08, AUTH-09) [wave 3, depends: 10-02]

### Phase 11: UX Redesign
**Goal**: Интерфейс работает как единое рабочее пространство — загрузка, навигация и чат в одном экране
**Depends on**: Phase 10
**Requirements**: UX-01, UX-02, UX-03, UX-04, UX-05, UX-06
**Success Criteria** (what must be TRUE):
  1. При входе пользователь сразу попадает в workspace (/ — главная страница), отдельной страницы загрузки нет
  2. Пользователь загружает файл через кнопку "+" в сайдбаре — модал загрузки, без смены страницы
  3. Новый пользователь без записей видит подсказку "Добавьте первую запись" в рабочей области
  4. Сообщения в чате отображаются пузырями: пользователь справа, AI слева, визуально различимы рамками и фоном
  5. Запись в процессе обработки показывает shimmer-анимацию на названии, а при наведении — прогресс-бар этапов (загрузка -> транскрипция -> диаризация -> готово)
**Plans**: TBD

Plans:
- [ ] 11-01-PLAN.md — Workspace как главная, модальная загрузка, empty state (UX-01, UX-02, UX-03) [wave 1]
- [ ] 11-02-PLAN.md — Чат-пузыри, shimmer-анимация, hover progress (UX-04, UX-05, UX-06) [wave 2, depends: 11-01]

### Phase 12: Unit Tests
**Goal**: Ключевая бизнес-логика data_ingress покрыта тестами — сервисы, репозитории, UoW и auth
**Depends on**: Phase 10 (auth code must exist to test)
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04
**Success Criteria** (what must be TRUE):
  1. pytest запускается одной командой и все тесты проходят (зелёный результат)
  2. RecordingService: тесты проверяют upload, получение списка записей, смену статусов
  3. UnitOfWork: тесты проверяют commit и rollback координацию (успех и ошибка)
  4. AuthService: тесты проверяют регистрацию, вход, верификацию токена (валидный и невалидный)
**Plans**: 2 plans

Plans:
- [ ] 12-01-PLAN.md — Инфраструктура pytest + тесты RecordingService и UnitOfWork (TEST-01, TEST-02) [wave 1]
- [ ] 12-02-PLAN.md — Тесты RecordingRepository и AuthService (TEST-03, TEST-04) [wave 2, depends: 12-01]

## Progress

**Execution Order:**
Phases execute in numeric order: 9 -> 10 -> 11 -> 12

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 2/2 | Complete | 2026-03-18 |
| 2. Core Analysis | v1.0 | 2/2 | Complete | 2026-03-19 |
| 3. FAQ | v1.0 | 2/2 | Complete | 2026-03-20 |
| 4. Chat with Transcript | v1.0 | 2/2 | Complete | 2026-03-22 |
| 5. Backend API | v1.1 | 2/2 | Complete | 2026-03-23 |
| 6. Frontend Scaffold | v1.1 | 2/2 | Complete | 2026-03-23 |
| 7. Upload & Processing | v1.1 | 2/2 | Complete | 2026-03-24 |
| 8. Workspace | v1.1 | 2/2 | Complete | 2026-03-25 |
| 9. Nginx Reverse Proxy | 2/2 | Complete   | 2026-03-28 | - |
| 10. JWT Authentication | 3/3 | Complete    | 2026-03-28 | - |
| 11. UX Redesign | 2/2 | Complete    | 2026-03-28 | - |
| 12. Unit Tests | v1.2 | 0/2 | Not started | - |
