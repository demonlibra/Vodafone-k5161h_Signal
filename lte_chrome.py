#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------- Импорт библиотек ---------------------------

import time
import re
import os
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome

import matplotlib.pyplot as plt

# ---------------------------- Параметры -------------------------------

url = 'http://192.168.9.1/html/content.html#deviceinformation'				# Адрес страницы с информацией о сигнале

max_mesuarements = 300																	# Максимальное количество измерений на графиках
period_refresh = 3																		# Период (секунд) получения данных. Указать 0 чтобы работать без задержек.

dir_result = 'graphics'																	# Каталог для сохранения результата
plot_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M") + '.png'	# Имя файла для сохранения

resolution = 150																			# Разрешение изображения (dpi)

# ----------------------------------------------------------------------

def get_value(marker):																	# Функция получения значений по маркеру
	string = driver.find_element(By.ID, marker).text
	value = re.search(r'(\-|)(\d+)(\.?)(\d*)', string).group(0)
	#print('string=', string, ' value=', value)
	return value

# ----------------------------------------------------------------------

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
				
			plt.text(x_time[i], y_text_postion, cell[i], horizontalalignment='left', verticalalignment=v_align)#   добавить на график номер базовой станции

# ----------------------------------------------------------------------

driver = Chrome(executable_path="chromedriver")									# Запуск браузера Chrome
driver.get(url)
driver.implicitly_wait(20)

if not os.path.exists(dir_result):
	os.makedirs(dir_result)

# ----------------------------------------------------------------------

unix_time_start = time.time()
x_time = []

cell = []	
rsrq = []
rsrp = []
rssi = []
sinr = []

while True:
	start_time = time.time()
	
	x_time.append(int(time.time()-unix_time_start))
	cell.append(str(get_value('di-cell_id')))
	rsrq.append(float(get_value('di-rsrq')))
	rsrp.append(int(get_value('di-rsrp')))
	rssi.append(int(get_value('di-rssi')))
	sinr.append(int(get_value('di-sinr')))

	x_time = x_time[-max_mesuarements:]
	cell = cell[-max_mesuarements:]
	rsrq = rsrq[-max_mesuarements:]
	rsrp = rsrp[-max_mesuarements:]
	rssi = rssi[-max_mesuarements:]
	sinr = sinr[-max_mesuarements:]

	#print('\nВремя извлечения данных =', round(time.time()-start_time, 2), 'сек')
	print(f'{x_time[0]}-{x_time[-1]}', datetime.datetime.now().strftime("%H-%M-%S"), 'CELL=' + str(cell[-1]), 'RSRQ=' + str(rsrq[-1]), 'RSRP=' + str(rsrp[-1]), 'RSSI=' + str(rssi[-1]), 'SINR=' + str(sinr[-1]))

	driver.find_element(By.ID, "dm-refresh").click()							# Нажатие кнопки "Обновить"
	
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

	cycle_time = time.time()- start_time											# Время выполнения цикла
	#print('Длительность цикла =', round(cycle_time, 2), 'сек')
	if period_refresh != 0:
		if period_refresh > cycle_time:
			time.sleep(period_refresh-cycle_time)
			#print('\nДлительность цикла =', round(time.time()- start_time, 3), 'сек. Минимальное время = ', round(cycle_time, 3), 'сек')
		else:
			print('Минимальное время', round(cycle_time, 2), 'больше заданного периода (period_refresh)', period_refresh)