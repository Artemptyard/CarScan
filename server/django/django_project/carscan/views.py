from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
import logging
import json
from typing import Dict
from pprint import pprint

# Глобальная переменная для хранения результата (не рекомендуется для production)
results = {}

# Create your views here.

@api_view(['GET', 'POST'])
def main_page(request):
    """"""
    logging.debug("Main page opened")
    return Response()

@api_view(['GET', 'POST'])
def cars_list(request):
    """"""
    if request.method == 'GET':
        data = Car.objects.all()
        serializer = CarSerializer(data, context={'request': request}, many=True)
        pprint(serializer.data[0])
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def cars_detail(request, pk):
    """"""
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CarSerializer(car)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def parsing(param: Dict[str, str], seconds: int = 10):
    """"""
    # Имитация длительного процесса
    time.sleep(seconds)
    result = f'Процесс завершён. Получен параметр param1 со значением: {param}'
    results[task_id] = result


# @csrf_exempt
@api_view(['POST'])
def parse(request):
    """"""
    if request.method == 'POST':
        data = json.loads(request.body)
        param = data.get('param1', None)
        if param1:
            # Генерация уникального идентификатора задачи
            task_id = str(time.time())
            # Запуск длительного процесса в отдельном потоке
            threading.Thread(target=long_running_task, args=(param1, task_id)).start()
            response_data = {'message': 'Процесс запущен', 'task_id': task_id}
        else:
            response_data = {'message': 'Параметр param1 не найден в запросе'}
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Только POST-запросы поддерживаются'}, status=400)


# @csrf_exempt
@api_view(['GET'])
def get_result(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id', None)
        if task_id and task_id in results:
            response_data = {'result': results.pop(task_id)}
        else:
            response_data = {'message': 'Результат не готов или task_id не найден'}

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Только GET-запросы поддерживаются'}, status=400)