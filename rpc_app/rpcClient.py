import json
import ssl
import urllib.request
import os
from typing import Any, Dict, Optional


class RpcClient:
    def __init__(self, endpoint: str, cert_data: str, key_data: str):
        self.endpoint = endpoint.strip()
        self.cert_data = cert_data.strip()
        self.key_data = key_data.strip()
        self._request_id = 1
        self._temp_files = []

    def _create_ssl_context(self) -> ssl.SSLContext:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # Отключаем проверку сертификата для тестового окружения
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            import tempfile
            # Сохраняем сертификат
            cert = tempfile.NamedTemporaryFile(mode='w', delete=False)
            cert.write(self.cert_data)
            cert.close()
            self._temp_files.append(cert.name)

            # Сохраняем ключ
            key = tempfile.NamedTemporaryFile(mode='w', delete=False)
            key.write(self.key_data)
            key.close()
            self._temp_files.append(key.name)

            context.load_cert_chain(cert.name, key.name)
            return context

        except Exception as e:
            self._cleanup_temp_files()
            raise Exception(f"Не удалось создать SSL контекст: {e}")

    def _cleanup_temp_files(self):
        for path in self._temp_files:
            try:
                os.remove(path)
            except OSError:
                pass  # игнорируем ошибки при очистке
        self._temp_files.clear()

    def call_method(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.endpoint:
            raise ValueError("Не указан URL сервера")

        req_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._request_id
        }

        try:
            ctx = self._create_ssl_context()
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(req_data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, context=ctx) as resp:
                result = json.loads(resp.read().decode())

            if "error" in result:
                raise Exception(f"Ошибка RPC: {result['error']}")

            return result.get("result", {})

        except json.JSONDecodeError:
            raise Exception("Некорректный JSON в ответе")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка соединения: {e}")
        except Exception as e:
            raise Exception(f"Ошибка запроса: {e}")
        finally:
            self._cleanup_temp_files()
            self._request_id += 1
