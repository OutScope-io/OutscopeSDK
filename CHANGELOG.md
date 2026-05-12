# Changelog

All notable changes to the OutScope SDK will be documented in this file.

## [0.3.1] - 2026-04-28

### Fixed
- Fixed report download URL generation (removed duplicate `/v1/` in path)
- `download()` now correctly constructs URL as `{base_url}/reports/{id}/download`
- `get_download_url()` now returns correct URL without duplication

### Impact
- Report downloads now work correctly from SDK
- URLs match the working Panel implementation

---

## [0.3.0] - 2026-04-28

### Added

#### New Resources
- **Assets Resource** (`client.assets`) - COMPLETE INVENTORY MANAGEMENT
  - **Asset CRUD:**
    - `create()` - Create asset manually with tags, metadata, company
    - `list()` - List assets with advanced filtering (search, tags, analyzability, company)
    - `get(asset_id)` - Get specific asset details
    - `update(asset_id, ...)` - Update asset properties
    - `delete(asset_id)` - Deactivate asset (soft delete)
  
  - **Schedule Management:**
    - `set_schedule(asset_id, schedule)` - Set recurring checks (hourly, daily, weekly)
  
  - **Check Integration:**
    - `trigger_check(asset_id)` - Manually trigger check for asset
    - `get_checks(asset_id)` - Get check history for asset
  
  - **Analytics:**
    - `get_stats()` - Get inventory statistics overview

### Features
- Complete asset inventory management
- Recurring check scheduling (hourly, daily, weekly)
- Manual check triggering per asset
- Advanced filtering (search, tags, analyzability, company)
- Asset lifecycle tracking (first_seen, last_seen, last_check)
- Company-scoped assets
- Check history per asset
- Inventory statistics and metrics
- Tag-based organization
- Custom metadata support

### Models
- Added `Asset` model with complete asset properties

### Documentation
- Added `examples/assets_usage.py` with comprehensive workflow demo
- Asset creation, scheduling, and monitoring examples

### Impact
- **Critical SaaS functionality enabled**
- Inventory management now available
- Automated recurring checks support
- Asset-centric workflows enabled

---

## [0.2.1] - 2026-04-28

### Added
- **Reports Resource** (`client.reports`)
  - Template management (CRUD)
  - Logo upload
  - Report generation (async)
  - Report download
  - Status tracking

---

## [0.2.0] - 2026-04-28

### Added
- **Worker Pools Resource** (`client.pools`)
- **Companies Resource** (`client.companies`)
- Enhanced Checks with advanced filtering
- Check lifecycle operations (cancel, review, latest)

### Changed
- **Breaking:** `include_content_sample` → `collect_content_sample`

---

## [0.1.2] - Initial Release

### Features
- Basic check operations
- Usage monitoring
- Batch operations

---

## Coverage Summary

| Version | Resources | Methods | API Coverage |
|---------|-----------|---------|--------------|
| 0.3.0   | 6         | 38      | ~61%         |
| 0.2.1   | 5         | 28      | ~45%         |
| 0.2.0   | 4         | 17      | ~37%         |
| 0.1.2   | 2         | 5       | ~11%         |

### Resource Coverage (v0.3.0)
- ✅ Checks (100% - 10 methods)
- ✅ Usage (100% - 1 method)
- ✅ Pools (100% - 1 method)
- ✅ Companies (100% - 5 methods)
- ✅ Reports (100% - 11 methods)
- ✅ Assets (100% - 10 methods)
- ⏳ Analytics (0% - planned for v0.4.0)
- ⏳ Support (0% - planned for v0.5.0)

---

## Roadmap

### v0.4.0 (Next - Analytics)
- Analytics resource (11 endpoints)
- Dashboard metrics and KPIs
- Timelines and trends
- Distributions and breakdowns

### v0.5.0 (Completeness)
- Support resource
- User info endpoints
- 90%+ API coverage

### v1.0.0 (Stability)
- 100% API coverage
- AsyncClient support
- Comprehensive test suite
- Performance optimizations
- LTS support commitment
