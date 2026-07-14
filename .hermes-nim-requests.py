import os, sys

def main():
    found = []
    found.append(("python_version", True, sys.version.split()[0]))
    for mod in ("requests", "openai", "numpy", "pandas"):
        try:
            m = __import__(mod, fromlist=["__version__"])
            v = getattr(m, "__version__", "unknown-installed")
            found.append((mod, True, v))
        except Exception as e:
            found.append((mod, False, str(e)))
    print("local validation only: no network calls")
    for name, ok, value in found:
        print(f"{'OK' if ok else 'FAIL'} {name}: {value}")

    def redact(v, n=8):
        if v is None:
            return "empty"
        if len(v) >= n:
            return v[:n] + "..."
        return v
    for key in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY", "KIMI_API_KEY", "NVIDIA_API_KEY",
                "OPENAI_BASE_URL", "NIM_CHAT_URL"):
        print(f"ENV {key}={redact(os.getenv(key))}")


if __name__ == "__main__":
    main()
