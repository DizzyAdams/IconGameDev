import os, sys

def main():
    checks = []
    checks.append(("python3", True, sys.version.split()[0]))
    checks.append(("requests", __import__("requests", fromlist=[""]).__version__ if False else None, None))
    try:
        from openai import OpenAI
        import importlib.metadata
        openai_version = importlib.metadata.version("openai")
        checks.append(("openai", True, openai_version))
    except Exception as e:
        checks.append(("openai", False, str(e)))

    print("local validation only: no network calls")
    for name, ok, value in checks:
        if value is None:
            value = "missing"
        print(f"{'OK' if ok else 'FAIL'} {name}: {value}")
    # surface env without echoing live keys
    def redact(v, n=8):
        return ("" if v is None else f"{v[:n]}...") if len(v or "") >= n else (v or "empty")
    for key in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY", "KIMI_API_KEY", "NVIDIA_API_KEY",
                "OPENAI_BASE_URL", "NIM_CHAT_URL"):
        print(f"ENV {key}={redact(os.getenv(key))}")


if __name__ == "__main__":
    main()
