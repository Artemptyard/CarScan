from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import *
import logging

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
        logging.debug("(GET) Loaded cars list")
        data = Car.objects.all()
        serializer = CarSerializer(data, context={'request': request}, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        logging.debug("(POST) Get updated cars")
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
def cars_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = CarSerializer(car)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)