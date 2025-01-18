from django.views.generic import FormView
from django.conf import settings
from .forms import RpcForm
from .rpcClient import RpcClient
import json


class RpcView(FormView):
    '''
    Класс для обработки запросов к RPC сервису
    '''
    template_name = 'rpc_app/rpc_form.html'
    form_class = RpcForm
    success_url = '/'

    def form_valid(self, form):
        try:
            params = {}
            if form.cleaned_data['params']:
                try:
                    params = json.loads(form.cleaned_data['params'])
                except json.JSONDecodeError:
                    form.result = {'error': 'Неверный формат JSON в параметрах'}
                    return self.render_to_response(self.get_context_data(form=form))

            client = RpcClient(
                settings.CLIENT_ENDPOINT,
                settings.CLIENT_CERT,
                settings.CLIENT_KEY
            )

            result = client.call_method(
                form.cleaned_data['method'],
                params
            )
            form.result = result
        except Exception as e:
            form.result = {'error': str(e)}

        return self.render_to_response(self.get_context_data(form=form))
