from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json
from .rpcClient import RpcClient


class RpcViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('rpc')

    def test_get_request_returns_form(self):
        """Проверяем, что GET-запрос возвращает форму"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rpc_app/rpc_form.html')
        self.assertContains(response, '<form')

    def test_post_invalid_json_params(self):
        """Проверяем обработку невалидного JSON"""
        data = {
            'method': 'auth.check',
            'params': 'некорректный { json'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неверный формат JSON в параметрах', response.content.decode())

    @patch('rpc_app.views.RpcClient')
    def test_successful_rpc_call(self, mock_client):
        """Проверяем успешный вызов RPC-метода"""
        # Настраиваем мок
        mock_instance = mock_client.return_value
        mock_instance.call_method.return_value = {'success': True}

        data = {
            'method': 'auth.check',
            'params': '{"param": "value"}'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')

        # Проверяем, что метод был вызван с правильными параметрами
        mock_instance.call_method.assert_called_once_with(
            'auth.check',
            {'param': 'value'}
        )

    @patch('rpc_app.views.RpcClient')
    def test_rpc_call_error(self, mock_client):
        """Проверяем поведение при ошибке RPC"""
        mock_rpc = mock_client.return_value
        mock_rpc.call_method.side_effect = Exception('Ошибка соединения')

        response = self.client.post(self.url, {
            'method': 'auth.check',
            'params': '{}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Ошибка соединения', response.content.decode())


class JsonRpcClientTests(TestCase):
    def setUp(self):
        self.api_url = 'https://api.example.org/v1'
        self.test_cert = '-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----'
        self.test_key = '-----BEGIN PRIVATE KEY-----\nMIIEv...\n-----END PRIVATE KEY-----'

    def test_client_initialization(self):
        """Проверяем корректную инициализацию клиента"""
        client = RpcClient(self.api_url, self.test_cert, self.test_key)
        self.assertEqual(client.endpoint, self.api_url)
        self.assertEqual(client._request_id, 1)

    @patch('urllib.request.urlopen')
    def test_successful_request(self, mock_urlopen):
        """Проверяем успешный запрос"""
        # Настраиваем мок для urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'result': {'success': True},
            'id': 1
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = RpcClient(self.api_url, self.test_cert, self.test_key)

        with patch('ssl.SSLContext'):  # Мокаем SSL-контекст
            result = client.call_method('test.method', {'param': 'value'})

        self.assertEqual(result, {'success': True})
        self.assertEqual(client._request_id, 2)  # Проверяем инкремент ID

    @patch('urllib.request.urlopen')
    def test_error_response(self, mock_urlopen):
        """Проверяем обработку ошибочного ответа от сервера"""
        # Настраиваем мок для возврата ошибки
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'error': {'code': -32600, 'message': 'Invalid Request'},
            'id': 1
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = RpcClient(self.api_url, self.test_cert, self.test_key)

        with patch('ssl.SSLContext'):
            with self.assertRaises(Exception) as context:
                client.call_method('test.method')

        self.assertIn('RPC Error', str(context.exception))
