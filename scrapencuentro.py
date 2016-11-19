#!/usr/bin/env python3
"""
Script en python3 para descargar las grillas mensuakes de encuentro

Leyendo la grilla del Canal Encuentro 
http://www.encuentro.gob.ar/sitios/encuentro/grilla/index?dia=01&mes=11&anio=2012&m=anterior#
puedo notar que las URLs para descargar la version PDF de las grillas es simple de replicar
Ejemplo: 1/11/2013
http://www.encuentro.gob.ar/sitios/encuentro/Grilla/descargarGrilla?dia=01&mes=11&anio=2013

"""

base_pdf = "http://www.encuentro.gob.ar/sitios/encuentro/Grilla/descargarGrilla"
import csv
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import requests
import os
import subprocess
from slugify import slugify

start_date = date(2013, 5, 1)
end_date = date(2016, 11, 6)  # date.today()

d = start_date

finalt = open("final.txt", "w")
finalcsv = "final.csv"
finald = []  # datos finales estructurados
ultimo_cargado = ""  # si un programa está dos veces seguidas entiendo que es por largo y no por doble

while d <= end_date:
	
	print(d.strftime("%Y-%m-%d"))
	dia = d.strftime("%d")
	mes = d.strftime("%m")
	anio = d.strftime("%Y")

	file_pdf = "grillaPDF/GrillaEncuentro-{}-{}-{}.pdf".format(dia, mes, anio)
	if os.path.isfile(file_pdf):
		print("OK")
	else:
		print("Descargando")
		url_pdf = "{}?dia={}&mes={}&anio={}".format(base_pdf, dia, mes, anio)
		r = requests.get(url_pdf)
		with open(file_pdf, 'wb') as f:
			f.write(r.content)

	file_txt = "grillaTXT/GrillaEncuentro-{}-{}-{}.txt".format(dia, mes, anio)
	if os.path.isfile(file_txt):
		print("Ya leido")
	else:
		print("Leyendo a txt")
		subprocess.call(["pdf2txt.py", '-o', file_txt, file_pdf])

	t = open(file_txt, 'r')
	contenido = t.read()
	finalt.write(contenido)
	t.close()

	# analizar el contenido, ver solo las líneas con datos

	for c in contenido.split("\n"):

		if len(c)> 5 and c[2] == ":" and c[5] == ":":
			partes = c.split(":")
			programa = ':'.join(partes[2:])
			# algunos están vacios, cargar sólo con datos
			if ultimo_cargado != programa and len(programa) > 3:
				ultimo_cargado = programa
				partes_programa = programa.split(' - ')
				programa_base = partes_programa[0].strip()
				programa_capitulo = ' - '.join(partes_programa[1:]).strip()
				
				# aprovecho para puntuar esto segun franjas horarias que
				# a mi criterio pueden marcar la importancia en el momento de emision
				hora = int(partes[0])
				wd = d.weekday()

				if wd > 0 and wd < 6: 
					if hora == 0:
						pts = 21
					elif hora > 0 and hora < 6:
						pts = 7
					elif hora >= 6 and hora < 13:
						pts = 11
					elif hora >= 13 and hora < 18:
						pts = 15
					elif hora >= 18 and hora < 21:
						pts = 21
					elif hora >= 21:
						pts = 27
				elif wd == 0 or wd == 6: 
					if hora == 0:
						pts = 24
					elif hora > 0 and hora < 6:
						pts = 11
					elif hora >= 6 and hora < 13:
						pts = 15
					elif hora >= 13 and hora < 18:
						pts = 19
					elif hora >= 18 and hora < 21:
						pts = 27
					elif hora >= 21:
						pts = 31
					
				if not programa_capitulo:
					programa_capitulo = 'todo'
				programa_base = slugify(programa_base)
				
				este = {"dia": dia, "mes": mes, "anio": anio,
						"hora": hora, "minuto": partes[1],
						"programa": programa_base,
						"capitulo": programa_capitulo,
						"pts": pts}
				finald.append(este)

	# d += relativedelta(months=+1)
	d += timedelta(days=+1)

finalt.close()

# imprimir a CSV y analizar datos mas finos
programas = {}

with open(finalcsv, 'w') as csvfile:
	# fieldnames = finald[0].keys()
	fieldnames = ["anio", "mes", "dia", "hora", "minuto", "programa", "capitulo", "pts"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in finald:
		# print(p)
		if p["programa"] not in programas.keys():
			programas[p["programa"]] = {'anios': {}, 'meses': {}}
		
		if p["anio"] not in programas[p["programa"]]['anios']:
			programas[p["programa"]]['anios'][p["anio"]] = {'cant': 0, 'pts': 0}

		programas[p["programa"]]['anios'][p["anio"]]['cant'] = programas[p["programa"]]['anios'][p["anio"]]['cant'] + 1
		programas[p["programa"]]['anios'][p["anio"]]['pts'] = programas[p["programa"]]['anios'][p["anio"]]['pts'] + p["pts"]

		mes = "{}-{}".format(p["anio"], p["mes"])
		if mes not in programas[p["programa"]]['meses']:
			programas[p["programa"]]['meses'][mes] = {'cant': 0, 'pts': 0}
		programas[p["programa"]]['meses'][mes]['cant'] = programas[p["programa"]]['meses'][mes]['cant'] + 1
		programas[p["programa"]]['meses'][mes]['pts'] = programas[p["programa"]]['meses'][mes]['pts'] + p["pts"]

		writer.writerow(p)

# grabar totales
with open("acumulado.csv", 'w') as csvfile:
	fieldnames = ["programa", "2013", "2014", "2015", "2016"]
	for a in range(2013, 2017):
		for m in range(1, 13):
			fieldnames.append("{0}-{1:02d}".format(a, m))

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		h2015 = a2013 + a2014 + a2015
		row = {"programa": p,
				"2013": a2013,
				"2014": a2014,
				"2015": a2015,
				"2016": a2016}
		
		for a in range(2013, 2017):
			for m in range(1, 13):
				mes = "{0}-{1:02d}".format(a, m)
				row[mes] = 0 if not mes in programas[p]['meses'] else programas[p]['meses'][mes]["pts"]

		writer.writerow(row)

# para streamgraph mensual
with open("viz/programas-por-mes/encuentro-streamgraph-mes.csv", 'w') as csvfile:
	fieldnames = ["key", "value", "date"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		tot = a2013 + a2014 + a2015 + a2016
		if tot < 5000:  # solo los más importantes
			continue;
		for a in range(2013, 2017):
			for m in range(1, 13):
				if a == 2013 and m < 5:
					continue
				if a == 2016 and m > 10:
					continue

				mes = "{0}-{1:02d}-01".format(a, m)
				mesdb = "{0}-{1:02d}".format(a, m)
				val = 0 if not mesdb in programas[p]['meses'] else programas[p]['meses'][mesdb]["pts"]

				row = {"key": p, "value": val, "date": mes}
				writer.writerow(row)

# para streamgraph anueal
with open("viz/programas-por-anio/encuentro-streamgraph-anio.csv", 'w') as csvfile:
	fieldnames = ["key", "value", "date"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		tot = a2013 + a2014 + a2015 + a2016
		if tot < 5000:  # solo los más importantes
			continue;
		for a in range(2013, 2017):
			# dia = "{}-01-01".format(a)
			anio = str(a)
			val = 0 if not anio in programas[p]['anios'] else programas[p]['anios'][anio]["pts"]

			row = {"key": p, "value": val, "date": anio}
			writer.writerow(row)


# Evolucion de los programas mas vistos en 2016 (Gestión Cambienos)
with open("viz/historia-programas-mas-vistos-2016/mes.csv", 'w') as csvfile:
	fieldnames = ["key", "value", "date"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		if a2016 < 1200:  # solo los más importantes
			continue;
		for a in range(2013, 2017):
			for m in range(1, 13):
				if a == 2013 and m < 5:
					continue
				if a == 2016 and m > 10:
					continue

				mes = "{0}-{1:02d}-01".format(a, m)
				mesdb = "{0}-{1:02d}".format(a, m)
				val = 0 if not mesdb in programas[p]['meses'] else programas[p]['meses'][mesdb]["pts"]

				row = {"key": p, "value": val, "date": mes}
				writer.writerow(row)

# Evolucion de los programas mas vistos en 2015 (Gestión FPV)
with open("viz/historia-programas-mas-vistos-2015/mes.csv", 'w') as csvfile:
	fieldnames = ["key", "value", "date"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		if a2015 < 1500:  # solo los más importantes
			continue;
		for a in range(2013, 2017):
			for m in range(1, 13):
				if a == 2013 and m < 5:
					continue
				if a == 2016 and m > 10:
					continue

				mes = "{0}-{1:02d}-01".format(a, m)
				mesdb = "{0}-{1:02d}".format(a, m)
				val = 0 if not mesdb in programas[p]['meses'] else programas[p]['meses'][mesdb]["pts"]

				row = {"key": p, "value": val, "date": mes}
				writer.writerow(row)


# Analizar los capitulos de un programa en especial
with open("viz/historia-programas-mas-vistos-2015/mes.csv", 'w') as csvfile:
	fieldnames = ["key", "value", "date"]

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

	for p in programas.keys():
		a2013 = 0 if not "2013" in programas[p]['anios'] else programas[p]['anios']["2013"]["pts"]
		a2014 = 0 if not "2014" in programas[p]['anios'] else programas[p]['anios']["2014"]["pts"]
		a2015 = 0 if not "2015" in programas[p]['anios'] else programas[p]['anios']["2015"]["pts"]
		a2016 = 0 if not "2016" in programas[p]['anios'] else programas[p]['anios']["2016"]["pts"]
		if a2015 < 1500:  # solo los más importantes
			continue;
		for a in range(2013, 2017):
			for m in range(1, 13):
				if a == 2013 and m < 5:
					continue
				if a == 2016 and m > 10:
					continue

				mes = "{0}-{1:02d}-01".format(a, m)
				mesdb = "{0}-{1:02d}".format(a, m)
				val = 0 if not mesdb in programas[p]['meses'] else programas[p]['meses'][mesdb]["pts"]

				row = {"key": p, "value": val, "date": mes}
				writer.writerow(row)

# imprimir a CSVs separados para graficos stackeando capitulos por programa
programas = {}
"""
{"dia": dia, "mes": mes, "anio": anio,
	"hora": hora, "minuto": partes[1],
	"programa": programa_base,
	"capitulo": programa_capitulo,
	"pts": pts}
"""
for p in finald:
	if p["programa"] not in programas.keys():
		programas[p["programa"]] = {}
	if p["capitulo"] not in programas[p["programa"]].keys():
		programas[p["programa"]][p["capitulo"]] = {}
	mes = '{}-{}'.format(p["anio"], p["mes"])
	if mes not in programas[p["programa"]][p["capitulo"]].keys():
		programas[p["programa"]][p["capitulo"]][mes] = p['pts']
	else:
		programas[p["programa"]][p["capitulo"]][mes] += p['pts']

base_path = 'viz/detalle-programas/data'
# escribir la lista de programas
csv_index = '{}/index.csv'.format(base_path)
with open(csv_index, 'w') as csvfile:
	fieldnames = ['file', 'name']

	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	ps = sorted(programas.keys())
	for p in ps:
		row = {'file': '{}.csv'.format(p), 'name': p}
		writer.writerow(row)

meses = []
for a in range(2013, 2017):
	for m in range(1, 13):
		if a == 2013 and m < 5:
			continue
		if a == 2016 and m > 10:
			continue
		mes = "{0}-{1:02d}".format(a, m)
		meses.append(mes)

# escribir cada CSV
for p in programas.keys():
	csv_file = '{}/{}.csv'.format(base_path, p)
	with open(csv_file, 'w') as csvfile:
		capitulos = list(programas[p].keys())
		print(capitulos)
		fieldnames = ["mes"] + capitulos  # nombre programa, capitulo1, capitulo2, etc
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		
		for m in meses:
			row = {"mes": m}
			for c in capitulos:  # capitulos
				if m not in programas[p][c].keys():
					val = 0
				else:
					val = programas[p][c][m]
				row[c] = val

			writer.writerow(row)
			
