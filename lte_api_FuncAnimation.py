#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------- Импорт библиотек ---------------------------

import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import os
import re
import requests
import time
import xml.etree.ElementTree as ET
import dbus

# ---------------------------- Параметры -------------------------------

URL_API = 'http://192.168.9.1/api/device/signal'								# Адрес страницы с информацией о сигнале
FILE_XML = 'signal.xml'

MAX_MESUAREMENTS = 200																	# Максимальное количество измерений на графиках
PERIOD_REFRESH = 500																		# Период (милисекунд) получения данных. Указать 0 чтобы работать без задержек.

DIR_RESULT = 'graphics'																	# Каталог для сохранения изображений
PLOT_NAME = f'{dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'		# Имя файла для сохранения изображения
IMG_RESOLUTION = 150																		# Разрешение изображения (dpi)

# ------------------------------ Функции -------------------------------

def send_notify(title, message):
	item = "org.freedesktop.Notifications"
	notify = dbus.Interface(dbus.SessionBus().get_object(item, "/"+item.replace(".", "/")), item)
	notify.Notify("", 0, "", title, message, [], {"urgency": 1}, 3000)
    
def get_value(marker):																	# Функция получения значений по маркеру
	string = tree.find(marker).text
	value = re.search(r'(\-|)(\d+)(\.?)(\d*)', string).group(0)
	#print('string=', string, ' value=', value)
	if (marker != 'cell_id') and (cell[-1] == 0):
		return None
	else:
		if "." in value: return float(value)
		else: return int(value)
		
def add_plot(position, data, y_min, y_max, title, units, level1, level2, level3):# Функция добавления графика
	axes = plt.subplot(2, 2, position)
	#plt.cla()
	
	xfmt = mdates.DateFormatter('%M:%S')
	axes.xaxis.set_major_formatter(xfmt)

	locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
	#locator = mdates.SecondLocator(bysecond=[0,30])
	axes.xaxis.set_major_locator(locator)
	
	plt.axhline(level1, color='yellow')
	plt.axhline(level2, color='orange')
	plt.axhline(level3, color='red')
	plt.title(title + ', ' + units)

	if x_time[-1] > x_time[0]:
		plt.xlim(d_time[0], d_time[-1])
	plt.ylim([y_min,y_max])
	plt.grid(True)																			# Показать сетку
	
	# Добавляем на график номер базовой станции
	flag_text_top = False
	for i in range(len(cell)):
		if (i == 0) or (cell[i] != cell[i-1] != 0):								# Если изменился номер базовой станции,
			plt.plot(d_time[i], data[i], 'r.')										#   добавить на график красную точку
			
			if cell[i] != 0:
				flag_text_top = not flag_text_top									# Смена позиции текста (номера базовой станции), чтобы не пересекались

			if flag_text_top:
				y_text_position = max(data)+(y_max-y_min)*0.02
				v_align = 'bottom'
			else:
				y_text_position = min(data)-(y_max-y_min)*0.02
				v_align = 'top'
			
			plt.text(d_time[i], y_text_position, cell[i], 
						horizontalalignment='left', verticalalignment=v_align)# Добавить на график номер базовой станции

	plt.plot(d_time, data, linewidth=1.0, color='blue')

	if cell[-1] != 0:
		plt.plot(d_time[-1], data[-1], 'g.')

		# Текущее значение справа от графика
		if data[-1] > level1: facecolor = 'green'
		elif data[-1] > level2: facecolor = 'yellow'
		elif data[-1] > level3: facecolor = 'orange'
		else: facecolor = 'red'
		bbox_props = dict(boxstyle='round', fc=facecolor, ec='black')
		axes.annotate(str(data[-1]), (d_time[-1], data[-1]), xytext=(10,0), textcoords='offset pixels', bbox=bbox_props)

def main_func(index):
	global tree

	#with open(FILE_XML) as file:
	#	xml_data = file.readlines()[0].replace(r'\r\n','',-1)
	xml_data = requests.get(URL_API).text
	tree = ET.XML(xml_data)

	x_time.append(int(time.time()))
	d_time.append(dt.datetime.fromtimestamp(x_time[-1]))
	cell.append(get_value('cell_id'))
	rsrq.append(get_value('rsrq'))
	rsrp.append(get_value('rsrp'))
	rssi.append(get_value('rssi'))
	sinr.append(get_value('sinr'))
	
	if len(x_time) > MAX_MESUAREMENTS:
		x_time.pop(0)
		d_time.pop(0)
		cell.pop(0)
		rsrq.pop(0)
		rsrp.pop(0)
		rssi.pop(0)
		sinr.pop(0)

	text_time = dt.datetime.now().strftime("%H-%M-%S")
	text_1 = (
		f'CELL={cell[-1]}'
		f' RSRQ={rsrq[-1]} RSRP={rsrp[-1]}'
		f' RSSI={rssi[-1]} SINR={sinr[-1]}')
	text_2 = (
		f'PCI={get_value("pci")}'
		f' MODE={get_value("mode")}'
		f' ulBandWidth={get_value("ulbandwidth")}'
		f' dlBandWidth={get_value("dlbandwidth")}'
		f' BAND={get_value("band")}'
		f' ULFREQ={get_value("ulfrequency")}'
		f' DLFREQ={get_value("dlfrequency")}')
	print(f'{text_time} {text_1} {text_2}')
	fig.clf()
	fig.suptitle(f'HUAWEI K5161H   {plot_title_time}   {text_2}')

	# position, data, y_min, y_max, title,                                 units, level1, level2, level3
	add_plot(1, rsrq, -21, 0, 'RSRQ - Качество принятых пилотных сигналов', 'dB', -10, -15, -20)
	add_plot(2, rsrp, -120, -70, 'RSRP - Уровень принимаемого сигнала с базовой станции', 'dBm', -80, -90, -100)
	add_plot(3, rssi, -115, -55, 'RSSI - Уровень мощности принимаемого сигнала', 'dBm', -65, -75, -85)
	add_plot(4, sinr, -22, 30, 'SINR - Cоотношение сигнал/шум', 'dB', 20, 13, 0)
	
	if (len(cell) == 1) or ((len(cell) > 1) and (cell[-1] != cell[-2])):
		send_notify('Смена базовой станции', str(cell[-1]))					# Отправить уведомление

# ----------------------------------------------------------------------

plot_title_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")			# Заголовок окна

x_time = []				# Время в формате UNIX Time
d_time = []				# Время datetime
cell = []
rsrq = []
rsrp = []
rssi = []
sinr = []

fig, ax = plt.subplots()
#plt.figure(figsize=(7*2, 3.5*2))
#fig.canvas.set_window_title('HUAWEI K5161H')

#plt.tight_layout()
fig.subplots_adjust(left=0.05, right=0.96, top=0.9, bottom=0.05, wspace=0.18, hspace=0.25)

#ani = FuncAnimation(plt.gcf(), main_func, interval=period_refresh, repeat=False)
ani = FuncAnimation(
		fig, main_func,
		interval=PERIOD_REFRESH, repeat=False)

plt.show()

if len(x_time) > 50:
	if not os.path.exists(DIR_RESULT):
		os.makedirs(DIR_RESULT)
	path_to_save = os.path.join(DIR_RESULT, PLOT_NAME)
	fig.savefig(path_to_save, dpi=IMG_RESOLUTION, pad_inches=0.2)