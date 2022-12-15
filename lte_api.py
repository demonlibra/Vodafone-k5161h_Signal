#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------- Импорт библиотек ---------------------------

import requests
import time
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import re
import datetime
import os

# ---------------------------- Параметры -------------------------------

url_api = 'http://192.168.9.1/api/device/signal'				# Адрес страницы с информацией о сигнале
file_xml = 'signal.xml'

max_mesuarements = 200																	# Максимальное количество измерений на графиках
period_refresh = 1																		# Период (секунд) получения данных. Указать 0 чтобы работать без задержек.

dir_result = 'graphics'																	# Каталог для сохранения результата
plot_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + '.png'	# Имя файла для сохранения

resolution = 150																			# Разрешение изображения (dpi)

def get_value(marker):																	# Функция получения значений по маркеру
	string = tree.find(marker).text
	value = re.search(r'(\-|)(\d+)(\.?)(\d*)', string).group(0)
	#print('string=', string, ' value=', value)
	return value

def add_plot(position, data, y_min, y_max, title, units, level1, level2, level3):# Функция добавления графика
	
	plt.subplot(2, 2, position)
	#plt.ylabel(units)
	#plt.xlabel('сек')
	plt.axhline(level1, color='yellow')
	plt.axhline(level2, color='orange')
	plt.axhline(level3, color='red')
	plt.title(title + ', ' + units)

	# Задание правого лимита оси X с масштабирование в начале
	if x_time[-1] == 0:
		x_lim1 = 1
	elif x_time[0] == 0:
		x_lim1 = x_time[-1] * 1.01
	else:
		x_lim1 = x_time[-1] + (x_time[-1] - x_time[-2])

	# Задание правого лимита оси X без масштабирования в начале
	x_lim2 = int(max_mesuarements * period_refresh)
	if x_lim2 < x_time[-1]:
		x_lim2 = x_time[-1] + (x_time[-1] - x_time[-2])
	
	plt.xlim(x_time[0], x_lim2)
	plt.ylim([y_min,y_max])
	plt.grid(True)																			# Показать сетку

	plt.plot(x_time, data, linewidth=1.2)

	# Добавляем на график номер базовой станции
	flag_text_position = False
	for i in range(1, len(cell)):
		if (i == 2) or (cell[i] != cell[i-1]):										# Если изменился номер базовой станции,
			plt.plot(x_time[i], data[i], 'r.')										#   добавить на график красную точку
			
			# Смена позиции текста (номера базовой станции), чтобы не пересекались
			flag_text_position = not flag_text_position
			if flag_text_position:
				y_text_postion = max(data)+(y_max-y_min)*0.02
				v_align = 'bottom'
			else:
				y_text_postion = min(data)-(y_max-y_min)*0.02
				v_align = 'top'
			
			text = (
				f'cell: {cell[i]}'
				f'\npci: {pci[i]}'
				f'\nmode: {mode[i]}'
				f'\nulbandwidth: {ulbandwidth[i]} МГц'
				f'\ndlbandwidth: {dlbandwidth[i]} МГц'
				f'\nband: {band[i]}'
				f'\nulfrequency: {ulfrequency[i]} кГц'
				f'\ndlfrequency: {dlfrequency[i]} кГц')
			plt.text(x_time[i], y_text_postion, cell[i], horizontalalignment='left', verticalalignment=v_align)#   добавить на график номер базовой станции

# ----------------------------------------------------------------------

if not os.path.exists(dir_result):
	os.makedirs(dir_result)
	
main_time_start = time.time()
x_time = []

cell = []	
rsrq = []
rsrp = []
rssi = []
sinr = []

pci = []
mode = []
ulbandwidth = []
dlbandwidth = []
band = []
ulfrequency = []
dlfrequency = []

while True:
	start_time = time.time()
	x_time.append(int(time.time()-main_time_start))
	
	xml_data = requests.get(url_api).text
	#with open(file_xml) as file:
	#	xml_data = file.readlines()[0].replace(r'\r\n','',-1)
	tree = ET.XML(xml_data)
	
	cell.append(str(get_value('cell_id')))
	rsrq.append(float(get_value('rsrq')))
	rsrp.append(int(get_value('rsrp')))
	rssi.append(int(get_value('rssi')))
	sinr.append(int(get_value('sinr')))
	
	pci.append(int(get_value('pci')))
	mode.append(int(get_value('mode')))
	ulbandwidth.append(int(get_value('ulbandwidth')))
	dlbandwidth.append(int(get_value('dlbandwidth')))
	band.append(int(get_value('band')))
	ulfrequency.append(int(get_value('ulfrequency')))
	dlfrequency.append(int(get_value('dlfrequency')))
	
	x_time = x_time[-max_mesuarements:]
	cell = cell[-max_mesuarements:]
	rsrq = rsrq[-max_mesuarements:]
	rsrp = rsrp[-max_mesuarements:]
	rssi = rssi[-max_mesuarements:]
	sinr = sinr[-max_mesuarements:]

	#print('\nВремя извлечения данных =', round(time.time()-start_time, 2), 'сек')
	print(f'{x_time[0]}-{x_time[-1]} {datetime.datetime.now().strftime("%H-%M-%S")} CELL={cell[-1]} RSRQ={rsrq[-1]} RSRP={rsrp[-1]} RSSI={rssi[-1]} SINR={sinr[-1]}')

	plt.figure(figsize=(7*2, 3.5*2))													# Размер графика в дюймах

	#position, data, y_min, y_max, title,                                  units, level1, level2, level3
	add_plot(1, rsrq, -21, 0, 'RSRQ - Качество принятых пилотных сигналов', 'dB', -10, -15, -20)
	add_plot(2, rsrp, -120, -70, 'RSRP - Уровень принимаемого сигнала с Базовой Станции', 'dBm', -80, -90, -100)
	add_plot(3, rssi, -115, -55, 'RSSI - Уровень мощности принимаемого модемом сигнала', 'dBm', -65, -75, -85)
	add_plot(4, sinr, -22, 30, 'SINR - Cоотношение сигнал/шум', 'dB', 20, 13, 0)

	plt.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05)		# Поля вокруг графика

	try:
		plt.savefig(os.path.join(dir_result, plot_name), dpi=resolution)
	except KeyboardInterrupt:
		plt.savefig(os.path.join(dir_result, plot_name), dpi=resolution)
		print('\nЗавершено исполнение сценария')
		exit()

	plt.close()
	#print('Время отрисовки графиков =', round(time.time()-start_time, 2), 'сек')

	cycle_time = time.time() - start_time											# Время выполнения цикла
	#print('Длительность цикла =', round(cycle_time, 2), 'сек')
	if period_refresh:
		if period_refresh > cycle_time:
			time.sleep(period_refresh-cycle_time)
			#print('\nДлительность цикла =', round(time.time()- start_time, 3), 'сек. Минимальное время = ', round(cycle_time, 3), 'сек')
		else:
			print('Минимальное время', round(cycle_time, 2), 'больше заданного периода (period_refresh)', period_refresh)