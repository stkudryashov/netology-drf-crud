from rest_framework import serializers
from logistic.models import *


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockProduct
        fields = ['id', 'product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        for position in positions:
            StockProduct.objects.create(
                stock=stock,
                product=position.get('product'),
                quantity=position.get('quantity'),
                price=position.get('price')
            )

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        for position in positions:
            if position.get('quantity') == 0:
                StockProduct.objects.filter(
                    product=position.get('product'),
                    stock=stock.id
                ).delete()
                continue

            StockProduct.objects.filter(
                product=position.get('product'),
                stock=stock.id
            ).update_or_create(
                defaults={
                    'stock': stock,
                    'product': position.get('product'),
                    'quantity': position.get('quantity'),
                    'price': position.get('price')
                }
            )

        return stock
