from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivymd.uix.screen import Screen
from kivymd.uix.list import OneLineListItem
from kivy.uix.image import Image
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel,MDIcon
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.datatables import MDDataTable
from datetime import datetime, date
from database import bd,clientes,notas,lista_precios
from kivy.metrics import dp
import pandas as pd
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCardSwipe, MDCard, MDSeparator
from kivy.animation import Animation
from kivymd.uix.list import MDList
from kivy.properties import StringProperty,BooleanProperty,NumericProperty,ObjectProperty
import os
import requests
import matplotlib
from kivymd.utils import asynckivy as ak
from kivymd.uix.menu import MDDropdownMenu
from kivy.core.clipboard import Clipboard
from kivy.config import Config
from kivy_garden.mapview import MapMarkerPopup
from PIL import Image, ImageDraw, ImageFont

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


def get_app():
    return MDApp.get_running_app()


def generateNota(data):
    imgBase = Image.open('assets/images/NOTA_ELECTRONICA.png')

    # Agregar texto a la imagen
    draw = ImageDraw.Draw(imgBase)
    fontNombre = ImageFont.truetype("Assets\\fonts\\Lato-Regular.ttf", 39)
    fontM = ImageFont.truetype("Assets\\fonts\\Lato-Regular.ttf", 23,)
    fontB = ImageFont.truetype("Assets\\fonts\\Lato-Bold.ttf", 25,)
    draw.text((85,274), data['usuario_name'], fill=(0, 0, 0), font=fontNombre)
    draw.text((306, 326), data['fecha'], fill=(0, 0, 0), font=fontM)
    draw.text((151, 359), data['index'], fill=(187, 0, 4), font=fontM)

    # Agregar tabla de servicios
    y = 495
    for articulo in data['articulos']:
        draw.text((68, y), '{:.1f}'.format(articulo['cantidad']), fill=(0, 0, 0), font=fontM)
        draw.text((214, y), '${:,.2f}'.format(articulo['precio']), fill=(0, 0, 0), font=fontM)
        draw.text((351, y), articulo['servicio'], fill=(0, 0, 0), font=fontM)
        draw.text((739, y), '${:,.2f}'.format(articulo['cantidad']*articulo['precio']), fill=(0, 0, 0), font=fontM)

        y += 35
    
    draw.text((536, y+68), "SUBTOTAL", fill=(0, 0, 0), font=fontM)
    draw.text((692, y+68), '${:,.2f}'.format(data['subtotal']), fill=(0, 0, 0), font=fontM)
    draw.text((587, y+107), "ENVÍO", fill=(0, 0, 0), font=fontM)
    draw.text((692, y+107), '${:,.2f}'.format(data['envio']), fill=(0, 0, 0), font=fontM)
    draw.text((509, y+146), "DESCUENTOS", fill=(0, 0, 0), font=fontM)
    draw.text((692, y+146), '${:,.2f}'.format(data['descuentos']), fill=(0, 0, 0), font=fontM)
    draw.text((470, y+186), "TOTAL A PAGAR", fill=(0, 0, 0), font=fontB)
    draw.text((692, y+186), '${:,.2f}'.format(data['total']), fill=(0, 0, 0), font=fontB)


    # Guardar imagen
    imgBase.save(f"C:\\Users\\kekew\\Desktop\\{data['usuario_name']}.png")
