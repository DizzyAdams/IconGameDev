"""UUID Manager — Gera e persiste UUIDs v4 para manifest.json."""
import uuid, json, os, time, threading

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'uuid_registry.json')

_thread_lock = threading.Lock()

class FileLock:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fd = None

    def acquire(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        start_time = time.time()
        while True:
            try:
                # O_CREAT: create if not exists
                # O_EXCL: error if already exists (atomic check)
                # O_WRONLY: write only
                self.fd = os.open(self.filepath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return True
            except OSError:
                if time.time() - start_time > 15:
                    try:
                        os.remove(self.filepath)
                    except OSError:
                        pass
                time.sleep(0.01)

    def release(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            try:
                os.remove(self.filepath)
            except OSError:
                pass
            self.fd = None

class UUIDManager:
    def __init__(self, registry_path=REGISTRY_PATH):
        self.registry_path = registry_path
        lock_path = self.registry_path + ".lock"
        with _thread_lock:
            lock = FileLock(lock_path)
            lock.acquire()
            try:
                self.registry = self._load()
            finally:
                lock.release()

    def _load(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            except (json.JSONDecodeError, ValueError, OSError):
                return {}
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)

    def get_or_create(self, context):
        lock_path = self.registry_path + ".lock"
        with _thread_lock:
            lock = FileLock(lock_path)
            lock.acquire()
            try:
                self.registry = self._load()
                if context in self.registry:
                    return self.registry[context]
                new_uuid = str(uuid.uuid4())
                while new_uuid in self.registry.values():
                    new_uuid = str(uuid.uuid4())
                self.registry[context] = new_uuid
                self._save()
                return new_uuid
            finally:
                lock.release()

    def pack_uuids(self, pack_key):
        return {
            'header': self.get_or_create(f'{pack_key}_header'),
            'module': self.get_or_create(f'{pack_key}_module'),
        }
