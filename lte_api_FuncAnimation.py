#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------- Импорт библиотек ---------------------------

import requests
import datetime
import re
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import xml.etree.ElementTree as ET
import os

# ---------------------------- Параметры -------------------------------

URL_API = 'http://192.168.9.1/api/device/signal'								# Адрес страницы с информацией о сигнале
FILE_XML = 'signal.xml'

MAX_MESUAREMENTS = 200																	# Максимальное количество измерений на графиках
PERIOD_REFRESH = 500																		# Период (милисекунд) получения данных. Указать 0 чтобы работать без задержек.
PLOT_TITLE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")		# Заголовок окна

DIR_RESULT = 'graphics'																	# Каталог для сохранения изображений
PLOT_NAME = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'	# Имя файла для сохранения изображения
IMG_RESOLUTION = 150																			# Разрешение изображения (dpi)

# ------------------------------ Функции -------------------------------

def get_value(marker):																	# Функция получения значений по маркеру
	string = tree.find(marker).text
	value = re.search(r'(\-|)(\d+)(\.?)(\d*)', string).group(0)
	#print('string=', string, ' value=', value)
	return value

def add_plot(position, data, y_min, y_max, title, units, level1, level2, level3):# Функция добавления графика
	plt.subplot(2, 2, position)
	plt.cla()
	plt.axhline(level1, color='yellow')
	plt.axhline(level2, color='orange')
	plt.axhline(level3, color='red')
	plt.title(title + ', ' + units)

	if x_time[-1] > x_time[0]:
		plt.xlim(x_time[0], x_time[-1])
	plt.ylim([y_min,y_max])
	plt.grid(True)																			# Показать сетку
	
	# Добавляем на график номер базовой станции
	flag_text_position = False
	for i in range(len(cell)):
		if (i == 0) or (cell[i] != cell[i-1]):										# Если изменился номер базовой станции,
			plt.plot(x_time[i], data[i], 'r.')										#   добавить на график красную точку
			
			# Смена позиции текста (номера базовой станции), чтобы не пересекались
			if cell[i] != '0': flag_text_position = not flag_text_position
			if flag_text_position:
				y_text_postion = max(data)+(y_max-y_min)*0.02
				v_align = 'bottom'
			else:
				y_text_postion = min(data)-(y_max-y_min)*0.02
				v_align = 'top'
			
			plt.text(x_time[i], y_text_postion, cell[i], horizontalalignment='left', verticalalignment=v_align) # Добавить на график номер базовой станции

	plt.plot(x_time, data, linewidth=1.0, color='blue')
	plt.plot(x_time[-1], data[-1], 'g.')
	
def main_func(index):
	global tree
	global x_time, cell, rsrq, rsrp, rssi, sinr
	global pci, mode, ulbandwidth, dlbandwidth, band, ulfrequency, dlfrequency
	#plt.clf()

	#with open(FILE_XML) as file:
	#	xml_data = file.readlines()[0].replace(r'\r\n','',-1)
	xml_data = requests.get(URL_API).text
	tree = ET.XML(xml_data)

	cell.append(str(get_value('cell_id')))
	rsrq.append(float(get_value('rsrq')))
	rsrp.append(int(get_value('rsrp')))
	rssi.append(int(get_value('rssi')))
	sinr.append(int(get_value('sinr')))
	x_time.append(round(float(time.time()-main_time_start),1))

	x_time = x_time[-MAX_MESUAREMENTS:]
	cell = cell[-MAX_MESUAREMENTS:]
	rsrq = rsrq[-MAX_MESUAREMENTS:]
	rsrp = rsrp[-MAX_MESUAREMENTS:]
	rssi = rssi[-MAX_MESUAREMENTS:]
	sinr = sinr[-MAX_MESUAREMENTS:]
	
	text = (
		f'{x_time[0]}-{x_time[-1]} {datetime.datetime.now().strftime("%H-%M-%S")} CELL={cell[-1]}'\
		f' RSRQ={rsrq[-1]} RSRP={rsrp[-1]} RSSI={rssi[-1]} SINR={sinr[-1]}'\
		f" PCI={get_value('pci')} MODE={get_value('mode')}"\
		f" ulBandWidth={get_value('ulbandwidth')} dlBandWidth={get_value('dlbandwidth')}"\
		f" BAND={get_value('band')} ULFREQ={get_value('ulfrequency')} DLFREQ={get_value('dlfrequency')}")
	print(text)
	
	# position, data, y_min, y_max, title,                                 units, level1, level2, level3
	add_plot(1, rsrq, -21, 0, 'RSRQ - Качество принятых пилотных сигналов', 'dB', -10, -15, -20)
	add_plot(2, rsrp, -120, -70, 'RSRP - Уровень принимаемого сигнала с Базовой Станции', 'dBm', -80, -90, -100)
	add_plot(3, rssi, -115, -55, 'RSSI - Уровень мощности принимаемого модемом сигнала', 'dBm', -65, -75, -85)
	add_plot(4, sinr, -22, 30, 'SINR - Cоотношение сигнал/шум', 'dB', 20, 13, 0)

if not os.path.exists(DIR_RESULT):
	os.makedirs(DIR_RESULT)

main_time_start = time.time()
x_time = []

cell = []
rsrq = []
rsrp = []
rssi = []
sinr = []

fig, ax = plt.subplots()
#fig.canvas.set_window_title('HUAWEI K5161H')
plt.suptitle(f'HUAWEI K5161H {PLOT_TITLE}')
plt.tight_layout()

#ani = FuncAnimation(plt.gcf(), main_func, interval=period_refresh, repeat=False)
ani = FuncAnimation(fig, main_func, interval=PERIOD_REFRESH, repeat=False)
plt.show()

#plt.figure(figsize=(7*2, 3.5*2))
#fig.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05)

if len(x_time) > 100:
	path_to_save = os.path.join(DIR_RESULT, PLOT_NAME)
	fig.savefig(path_to_save, dpi=IMG_RESOLUTION, pad_inches=0.2)