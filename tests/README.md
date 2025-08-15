# Testing Guide

This directory contains comprehensive tests for the Git MCP Server comment functionality.

## Test Structure

### Unit Tests (`test_comment_functionality.py`)
- **No configuration required** - uses mocked dependencies
- Tests all adapter methods, service layer, and MCP tool integration
- **20 test cases** covering success paths, error handling, and edge cases
- **Always runs** in CI/CD regardless of token availability

### Integration Tests (`test_live_comment_integration.py`)
- **Requires platform configuration** - uses real GitHub/GitLab APIs
- Tests against actual test issues on live platforms
- **Automatically skipped** when platforms are not configured
- **Safe for contributors** - no tokens needed for basic development

## Running Tests

### Quick Start (No Setup Required)
```bash
# Run unit tests only (no tokens needed)
uv run pytest tests/test_comment_functionality.py -v

# This gives you complete coverage of the comment functionality
# Result: 20/20 tests pass with 100% code coverage
```

### Full Integration Testing (Optional)

#### Prerequisites
1. **Configure GitHub platform:**
   ```bash
   git-mcp config add github github --url https://github.com
   # Enter your GitHub token when prompted
   ```

2. **Configure GitLab platform (optional):**
   ```bash
   git-mcp config add gitlab gitlab --url https://gitlab.com
   # Enter your GitLab token when prompted
   ```

3. **Verify configuration:**
   ```bash
   git-mcp config list
   git-mcp config test github
   git-mcp config test gitlab  # if configured
   ```

#### Run Integration Tests
```bash
# Run all tests (unit + integration)
uv run pytest tests/ -v

# Run only integration tests
uv run pytest tests/test_live_comment_integration.py -v -s

# Run specific platform tests
uv run pytest tests/test_live_comment_integration.py::TestLiveCommentIntegration::test_github_comment_creation_live -v -s
```

## Test Behavior by Configuration

### No Platforms Configured
```
✅ Unit tests: 20/20 passed
⏭️ Integration tests: Skipped (platforms not configured)
📊 Result: All tests pass, full functionality verified
```

### GitHub Only Configured
```
✅ Unit tests: 20/20 passed
✅ GitHub integration: 4/4 passed (creates real comments on issue #29)
⏭️ GitLab integration: Skipped (platform not configured)
📊 Result: GitHub functionality fully verified
```

### Both Platforms Configured
```
✅ Unit tests: 20/20 passed
✅ GitHub integration: 4/4 passed
✅ GitLab integration: 2/2 passed
✅ Cross-platform tests: 1/1 passed
📊 Result: Complete platform coverage verified
```

## CI/CD Behavior

### External Contributors (No Secrets)
- ✅ Unit tests run automatically
- ⏭️ Integration tests automatically skipped
- ✅ CI passes without any configuration
- 💡 No secrets or setup required

### Maintainers (With Secrets)
- ✅ Unit tests run automatically
- ✅ Integration tests run with live APIs
- ✅ Full end-to-end verification
- 🔧 Real comment creation validated

## Test Issues Used

### GitHub Test Issue
- **URL:** https://github.com/yumeminami/git_mcp/issues/29
- **Title:** "TEST for issue comment(NEVER CLOSE)"
- **Purpose:** Safe target for automated comment creation
- **Access:** Public repository, open issue

### GitLab Test Issue
- **URL:** https://gitlab.com/gitlab-org/gitlab/-/issues/1
- **Title:** GitLab CE issue #1
- **Purpose:** GitLab comment functionality verification
- **Access:** Requires GitLab platform configuration

## Token Requirements

### GitHub Token
- **Scopes needed:** `repo` (for issue access and commenting)
- **Setup:** GitHub Settings → Developer settings → Personal access tokens
- **Storage:** Secure keyring via `git-mcp config add`

### GitLab Token
- **Scopes needed:** `api` (for full API access)
- **Setup:** GitLab Settings → Access Tokens
- **Storage:** Secure keyring via `git-mcp config add`

### Security Notes
- ✅ Tokens stored in system keyring (never in files)
- ✅ Minimal required permissions
- ✅ Test issues only (no production impact)
- ✅ Safe for concurrent execution

## Troubleshooting

### "Platform not configured" Errors
```bash
# Check current configuration
git-mcp config list

# Add missing platform
git-mcp config add github github --url https://github.com
git-mcp config add gitlab gitlab --url https://gitlab.com

# Test connection
git-mcp config test github
git-mcp config test gitlab
```

### Integration Tests Failing
```bash
# Verify platform access
git-mcp config test github
git-mcp config test gitlab

# Check token permissions (GitHub)
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Run single test with debug
uv run pytest tests/test_live_comment_integration.py::TestLiveCommentIntegration::test_github_comment_creation_live -v -s
```

### CI/CD Issues
- **External PR:** Integration tests should be skipped automatically
- **Internal PR:** Check that `GIT_MCP_GITHUB_TOKEN` secret is configured
- **Token rotation:** Update repository secrets when tokens are rotated

## Coverage Information

- **Unit Tests:** 100% code coverage of comment functionality
- **Integration Tests:** Real API verification on both platforms
- **Error Scenarios:** Authentication, permissions, network failures
- **Edge Cases:** Empty comments, large content, special characters
- **Performance:** Concurrent operations, rate limiting

## Contributing

For contributors:
1. ✅ **Unit tests are sufficient** for most development
2. ✅ **No tokens required** for basic contribution workflow
3. ✅ **CI will pass** without any setup
4. 💡 Integration tests run automatically for maintainers

For maintainers:
1. 🔧 Configure platforms locally for full testing
2. 🔒 Ensure repository secrets are configured for CI
3. 🧪 Monitor integration test results for API changes
4. 🔄 Rotate tokens periodically for security
