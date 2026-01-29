import os
import re

# Adjust paths relative to this script location (docs/scripts)
# Script is in docs/scripts, so project root is ../../
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
TARGET_DIR = os.path.join(PROJECT_ROOT, "app/templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "app/static/css")

def audit_files():
    print(f"🚀 Starting Web Design Guidelines Audit...")
    print(f"📂 Project Root: {PROJECT_ROOT}\n")
    
    findings = []
    
    # Check if dirs exist
    if not os.path.exists(TARGET_DIR):
        print(f"Skipping template check: {TARGET_DIR} not found")
        return

    # 1. Anti-pattern: transition: all
    print("🔍 Checking CSS for 'transition: all'...")
    if os.path.exists(STATIC_DIR):
        for root, _, files in os.walk(STATIC_DIR):
            for file in files:
                if file.endswith((".css", ".scss")):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "transition: all" in content:
                            findings.append(f"🔴 [Animation] 'transition: all' found in {file}. Use specific properties.")

    # 2. Anti-pattern: outline-none without replacement
    print("🔍 Checking Templates for focus accessibility...")
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "outline-none" in content and "focus:" not in content:
                         findings.append(f"⚠️  [A11y] 'outline-none' potentially without replacement in {file}")

    # 3. Anti-pattern: Images without dimensions
    print("🔍 Checking Images for explicit dimensions...")
    img_regex = re.compile(r'<img[^>]+>')
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    imgs = img_regex.findall(content)
                    for img in imgs:
                        if "width=" not in img or "height=" not in img:
                             # Skip if using tailwind classes w- and h- (heuristic)
                             if "w-" not in img or "h-" not in img:
                                findings.append(f"⚠️  [Performance] Image tag missing width/height in {file}: {img[:40]}...")

    # 4. Form accessibility
    print("🔍 Checking Forms for autocomplete...")
    input_regex = re.compile(r'<input[^>]+>')
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    inputs = input_regex.findall(content)
                    for inp in inputs:
                         # Basic heuristic: check text/email inputs
                         if ('type="text"' in inp or 'type="email"' in inp) and 'type="hidden"' not in inp:
                             if "autocomplete=" not in inp:
                                  findings.append(f"⚠️  [Forms] Input missing autocomplete in {file}: {inp[:40]}...")

    print("\n📝 Audit Results:")
    if not findings:
        print("✅ No critical issues found! Great job.")
    else:
        for finding in findings:
            print(finding)
        print(f"\nTotal findings: {len(findings)}")

if __name__ == "__main__":
    audit_files()
