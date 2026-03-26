# GitHub Actions Workflows

## test-clone-scripts.yml

Automated testing for repository clone scripts across platforms.

### Overview

This workflow tests all three cloning scripts (`clone-tidymodels-repos.sh`, `clone-tidymodels-repos.ps1`, `clone-tidymodels-repos.py`) to ensure they work correctly on their target platforms.

### Triggers

- **Push**: When changes are pushed to `main` or `updates` branches affecting:
  - `tidymodels/shared-scripts/**`
  - `.github/workflows/test-clone-scripts.yml`
- **Pull Request**: When PRs target `main` branch with changes to the above paths
- **Manual**: Via GitHub Actions UI (workflow_dispatch)

### Test Matrix

| Job | Platform | Script | Python Versions |
|-----|----------|--------|----------------|
| test-bash-macos | macOS | Bash | N/A |
| test-bash-linux | Ubuntu | Bash | N/A |
| test-powershell-windows | Windows | PowerShell | N/A |
| test-python | All (Ubuntu, macOS, Windows) | Python | 3.8, 3.11 |

**Total test combinations**: 9 (Bash×2 + PowerShell×1 + Python×6)

### Tests Performed

#### All Scripts

1. **No arguments test**: Verify script exits with code 1
2. **Clone yardstick**: Test single package cloning
3. **Verify clone**:
   - Repository directory exists
   - R files directory exists
   - Shallow clone verified (.git/shallow)
   - .gitignore contains `repos/`
   - .Rbuildignore contains `^repos$`
4. **Idempotency**: Run script again on existing clone
5. **No duplicates**: Verify ignore files have no duplicate entries
6. **Clone all**: Test cloning all packages
7. **Verify all**: Check both yardstick and recipes cloned

#### Platform-Specific

**macOS/Linux (Bash)**:
- Uses `/tmp` for test directory
- Checks file permissions
- Tests bash 3.2+ compatibility (macOS)
- Tests bash 4.0+ features (Linux)

**Windows (PowerShell)**:
- Uses `$env:TEMP` for test directory
- Tests PowerShell 5.1+ compatibility
- Verifies CRLF line endings in ignore files
- Tests Windows path separators

**All Platforms (Python)**:
- Tests Python 3.8 and 3.11
- Verifies cross-platform compatibility
- Tests line ending handling per platform

### Success Criteria

A test passes if:
- ✅ Script executes without errors
- ✅ Repository is cloned to `repos/` directory
- ✅ Shallow clone is created (.git/shallow exists)
- ✅ .gitignore is created/updated with `repos/`
- ✅ .Rbuildignore is created/updated with `^repos$`
- ✅ Running script again doesn't create duplicates
- ✅ All packages clone when using "all" parameter

### Viewing Results

1. Navigate to **Actions** tab in GitHub repository
2. Click on **Test Repository Clone Scripts** workflow
3. View individual job results
4. Check **Summary** for overall pass/fail status

### Expected Output

**When all tests pass**:
```
✅ All tests passed successfully!

| Script | Platform | Status |
|--------|----------|--------|
| Bash | macOS | ✅ Passed |
| Bash | Linux | ✅ Passed |
| PowerShell | Windows | ✅ Passed |
| Python | All platforms | ✅ Passed |
```

**If any test fails**:
```
⚠️ Some tests failed. Please review the logs above.
```

### Debugging Failed Tests

If tests fail:

1. **Check the job logs**:
   - Click on the failed job
   - Expand each step to see detailed output
   - Look for error messages (marked with ✗)

2. **Common issues**:
   - **Git not found**: Unlikely in CI, but check runner setup
   - **Network timeout**: GitHub Actions may have network issues
   - **Permission error**: Check file permissions in script
   - **Platform-specific bug**: Review platform-specific code

3. **Reproduce locally**:
   ```bash
   # macOS/Linux
   cd /tmp && mkdir test && cd test
   ./tidymodels/shared-scripts/clone-tidymodels-repos.sh yardstick

   # Windows (PowerShell)
   cd $env:TEMP; New-Item -ItemType Directory test; cd test
   .\shared-scripts\clone-tidymodels-repos.ps1 yardstick
   ```

### Manual Triggering

To manually run tests:

1. Go to **Actions** tab
2. Click **Test Repository Clone Scripts**
3. Click **Run workflow** button
4. Select branch
5. Click **Run workflow**

### Maintenance

When updating scripts:
- Workflow automatically runs on push to `main`/`updates`
- Check workflow status before merging PRs
- Update test cases if script behavior changes
- Adjust timeouts if cloning takes longer

### Performance

**Typical run time**:
- Bash on macOS: ~2-3 minutes
- Bash on Linux: ~2-3 minutes
- PowerShell on Windows: ~3-4 minutes
- Python (6 combinations): ~15-20 minutes total

**Total workflow time**: ~20-25 minutes (runs in parallel)

### Future Enhancements

Potential improvements:
- [ ] Cache git clones to speed up tests
- [ ] Test with different git versions
- [ ] Add performance benchmarks
- [ ] Test network failure scenarios
- [ ] Add code coverage reporting

### Related Documentation

- [Test Clone Scripts Workflow](.github/workflows/test-clone-scripts.yml)
- [Phase 1 Summary](.github/PHASE_1_SUMMARY.md)
- [Repository Access Guide](../developers/shared-references/repository-access.md)
- [Scripts README](../developers/shared-scripts/README.md)
