"""
Script to stage and commit files locally using Dulwich.
"""
from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo

repo_path = "."
r = Repo(repo_path)

# List of files to track
tracked_extensions = {".py", ".md", ".txt", ".toml", ".yml", ".yaml", ".json", ".example", ".bat", "Dockerfile"}
files_to_add = []

for p in Path(repo_path).rglob("*"):
    # Skip ignored directories
    parts = p.parts
    if any(ignored in parts for ignored in [".git", ".venv", "__pycache__", ".pytest_cache", "uploads", "generated_reports"]):
        continue
    if p.is_file():
        if p.name == ".gitignore" or p.suffix in tracked_extensions or p.name == "Dockerfile":
            rel_path = str(p.relative_to(repo_path)).replace("\\", "/")
            files_to_add.append(rel_path)

print(f"Adding {len(files_to_add)} files to git...")
porcelain.add(r, files_to_add)

# Commit
commit_id = porcelain.commit(
    r,
    message=b"feat: complete production release of MARINE-SHIELD web application",
    author=b"MARINE-SHIELD Team <marine.shield@example.com>",
    committer=b"MARINE-SHIELD Team <marine.shield@example.com>"
)
print("Initial commit created successfully:", commit_id.decode())

# Ensure default branch is named 'main'
r.refs[b'refs/heads/main'] = commit_id
if b'refs/heads/master' in r.refs:
    del r.refs[b'refs/heads/master']
r.refs.set_symbolic_ref(b'HEAD', b'refs/heads/main')
print("Active branch set to 'main'.")
