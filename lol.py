import os

# Các thư mục cần xử lý
TARGET_DIRS = [
    "app",
    "features",
]

def ensure_init_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        init_path = os.path.join(root, "__init__.py")
        if "__pycache__" in root:
            continue

        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("")   # file rỗng
            print(f"✔ Created: {init_path}")

        # xử lý luôn subfolder
        for d in dirs:
            sub = os.path.join(root, d)
            sub_init = os.path.join(sub, "__init__.py")
            if not os.path.exists(sub_init):
                with open(sub_init, "w", encoding="utf-8") as f:
                    f.write("")  
                print(f"✔ Created: {sub_init}")


if __name__ == "__main__":
    for folder in TARGET_DIRS:
        if os.path.exists(folder):
            ensure_init_files(folder)
        else:
            print(f"⚠ Folder not found: {folder}")
