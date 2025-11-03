# Motivator Bot - Cleanup & Improvement Tasks

This file tracks cleanup and improvement tasks for the Motivator Bot project.

## Status Legend
- 🔴 High Priority
- 🟡 Medium Priority
- 🟢 Low Priority
- ✅ Completed

---

## High Priority

### ✅ Remove Deprecated Code
- [x] Delete `src/scheduler.py` - superseded by `smart_scheduler.py` (131 lines of dead code)

---

## Medium Priority

### 🟡 Refactor Large Files
**Issue**: `src/bot.py` is 2,070 lines - too large and monolithic

**Recommendation**: Split into separate modules
- [ ] Create `handlers/user_commands.py` (start, help, settings, pause, resume)
- [ ] Create `handlers/mood_commands.py` (mood, stats)
- [ ] Create `handlers/goal_commands.py` (goals)
- [ ] Create `handlers/admin_commands.py` (admin_*)
- [ ] Create `handlers/callbacks.py` (button callbacks)
- [ ] Create `services/` package for business logic:
  - `services/mood_service.py`
  - `services/goal_service.py`
  - `services/message_service.py`
- [ ] Refactor `MotivatorBot` class to be orchestrator, not handler container

**Estimated Effort**: 2-4 hours
**Impact**: High (maintainability, testability)

---

### 🟡 Implement Proper Test Suite
**Issue**: Only manual test scripts exist, no automated testing

**Current State**:
- `tests/test_message.py` (48 lines) - manual script
- `tests/test_persistence.py` (38 lines) - manual script
- Tests use hardcoded user IDs in actual database

**Recommendations**:
- [ ] Set up pytest framework with `pytest.ini` or `pyproject.toml`
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Add unit tests for database operations
- [ ] Add integration tests for bot handlers with mocked Telegram API
- [ ] Create test fixtures for database
- [ ] Document manual testing scripts in `docs/examples/` OR convert to automated tests

**Estimated Effort**: 4-8 hours
**Impact**: Medium (code confidence, regression prevention)

---

### 🟡 Content Management Strategy
**Issue**: Unclear content management approach - both hardcoded and database import system exist

**Current State**:
- Content is hardcoded in `src/content.py` (177 lines)
- `scripts/import_content.py` exists (213 lines) but not integrated
- `config/content_example.json` example file exists
- Database has content tables but may not be used

**Decision Required**: Choose ONE approach

**Option A - Keep Hardcoded** (if content is stable):
- [ ] Remove or document `import_content.py` as legacy tool
- [ ] Update `content_example.json` to match actual content in code
- [ ] Add inline documentation to `content.py`

**Option B - Use Database Import** (if content changes frequently):
- [ ] Migrate all content from `content.py` to database
- [ ] Integrate `import_content.py` into main workflow
- [ ] Create admin interface for content management
- [ ] Remove hardcoded content arrays from `content.py`

**Estimated Effort**: 2-4 hours
**Impact**: Medium (content flexibility, ease of updates)

---

### 🟡 Centralize Logging Configuration
**Issue**: Logging configured in multiple places, no rotation, not configurable

**Current Issues**:
- Both `main.py` and `bot.py` configure logging independently
- No log rotation for long-running deployments
- Log level not configurable via environment variable
- No structured logging (JSON format)

**Recommendations**:
- [ ] Create `src/logging_config.py` for centralized configuration
- [ ] Add `LOG_LEVEL` environment variable to `.env.example`
- [ ] Implement log rotation (using `RotatingFileHandler` or `TimedRotatingFileHandler`)
- [ ] Consider structured logging for easier parsing

**Estimated Effort**: 1 hour
**Impact**: Low (code quality, operational visibility)

---

## Low Priority

### 🟢 Expand Configuration Documentation
**Issue**: `.env.example` is minimal (only 2 variables)

**Recommendations**:
- [ ] Add comments explaining each variable
- [ ] Document optional environment variables:
  - `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)
  - `DATABASE_PATH` (custom database location)
  - `TIMEZONE` (user timezone examples)
- [ ] Add reference links to documentation sections

**Estimated Effort**: 15 minutes
**Impact**: Low (documentation, user experience)

---

### 🟢 Complete Documentation
**Missing Documentation**:
- [ ] Generate API documentation (docstrings + Sphinx or mkdocs)
- [ ] Create `docs/database_schema.md` with visual schema diagram
- [ ] Create `docs/contributing.md` for development guidelines
- [ ] Create `docs/troubleshooting.md` (some content exists in CLAUDE.md)
- [ ] Complete ADMIN_README.md examples (file has incomplete table)
- [ ] Add `CHANGELOG.md` for version history
- [ ] Consider `CODE_OF_CONDUCT.md` (important for mental health project)

**Estimated Effort**: 2-3 hours
**Impact**: Medium (usability, contributor onboarding)

---

### 🟢 Database Migration System
**Issue**: No schema versioning or migration system

**Current State**:
- Schema created in `database.py` `init_database()` method
- Adding new fields requires manual ALTER TABLE
- No version tracking for schema changes
- Difficult to deploy updates to existing installations

**Recommendations**:
- [ ] Implement simple migration system (Alembic or manual scripts in `scripts/migrations/`)
- [ ] Add schema version tracking in database
- [ ] Create migration scripts for future schema changes
- [ ] Document migration process in README.md

**Estimated Effort**: 3-4 hours
**Impact**: Medium (deployability, upgrade path)

---

### 🟢 Add Missing Project Files
**Standard Python project files that are absent**:
- [ ] `setup.py` or `pyproject.toml` - Package metadata
- [ ] `pytest.ini` or update `pyproject.toml` - Test configuration
- [ ] `Makefile` - Common development commands (install, test, run, clean)
- [ ] `.github/workflows/` - CI/CD pipeline (if using GitHub)
- [ ] `CHANGELOG.md` - Version history
- [ ] `CODE_OF_CONDUCT.md` - For mental health focused project

**Estimated Effort**: 1-2 hours
**Impact**: Low (project professionalism, automation)

---

## Git Configuration (User Responsibility)

### `.venv/` in Repository
**Issue**: Virtual environment directory may be tracked by git

**Note**: User confirmed this is already handled correctly in `.gitignore`

If needed in future:
```bash
# Add to .gitignore
echo ".venv/" >> .gitignore

# Remove from git history
git rm -r --cached .venv
git commit -m "Remove .venv from repository"
```

---

## Notes

- This TODO list is based on comprehensive codebase analysis
- Tasks can be prioritized based on project needs
- Some tasks are interdependent (e.g., refactoring before testing)
- Estimated effort times are approximate

**Last Updated**: 2025-11-02
