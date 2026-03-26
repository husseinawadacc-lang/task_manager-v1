import os
import shutil
import subprocess

print("🚀 Running Pre-Release Checks...\n")

# =========================================
# 1. Check .env file
# =========================================
if os.path.exists(".env"):
    print("❌ WARNING: .env file exists!")
else:
    print("✅ .env not found")

# =========================================
# 2. Remove __pycache__
# =========================================
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        shutil.rmtree(os.path.join(root, "__pycache__"))
        print(f"🧹 Removed __pycache__ in {root}")

# =========================================
# 3. Remove SQLite DB (لو موجود)
# =========================================
for file in os.listdir("."):
    if file.endswith(".db"):
        os.remove(file)
        print(f"🧹 Removed DB file: {file}")

# =========================================
# 4. Check logs folder
# =========================================
if os.path.exists("logs"):
    shutil.rmtree("logs")
    print("🧹 Logs folder removed")

# =========================================
# 5. Redis flush (اختياري)
# =========================================
try:
    subprocess.run(["redis-cli", "FLUSHALL"], check=True)
    print("🧹 Redis cleared")
except Exception:
    print("⚠️ Redis not cleared (skip)")

# =========================================
# 6. Check for secrets in code
# =========================================
danger_words = ["SECRET_KEY", "password", "token"]

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                for word in danger_words:
                    if word in content:
                        print(f"⚠️ Found '{word}' in {path}")

print("\n✅ Pre-release check done!")