# GitHub Repository Setup Plan

## Goal
Initialize a local git repository for the "Stocks Database" project and push it to a new GitHub repository.

## Steps

1.  **Initialize Git**: Run `git init` if not already initialized.
2.  **Create .gitignore**: Ensure sensitive files and virtual environments (`.venv`, `__pycache__`, `*.db` maybe? No, user might want the DB, but usually binary large files are bad. `stocks.db` is 115MB. GitHub limit is 100MB. Block `stocks.db` and maybe provide a seed script or instructions.)
    *   *Decision*: Ignore `stocks.db`. It's too large and derived data.
    *   Ignore `.venv`, `__pycache__`, `.DS_Store`.
3.  **Commit Files**: Stage all files (respecting .gitignore) and create initial commit.
4.  **Create GitHub Repo**: *Action Required from User*: Create a new empty repository on GitHub manually.
5.  **Push**:
    - Ask user for the repository URL.
    - Run `git remote add origin <url>`.
    - Run `git push -u origin main`.

## Verification
- `git status` should be clean.
- Code should be visible on GitHub.
