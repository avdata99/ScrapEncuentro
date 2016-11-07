# ScrapEncuentro
Datos en base a scrape sobre la programación diaria del Canal de TV Encuentro (AR)  


<p align="center">
  <img src="https://raw.githubusercontent.com/avdata99/ScrapEncuentro/master/static/viz1test.png" width="550"/>
</p>

La grilla se encuentra disponible en:  
http://www.encuentro.gob.ar/sitios/encuentro/grilla/index  

Para cada día hay un PDF bastante feo. Este es un ejemplo:  
https://github.com/avdata99/ScrapEncuentro/blob/master/grillaPDF/GrillaEncuentro-01-01-2014.pdf  

El script pasa los datos a TXT y luego a CSV específicos con datos utilizables.  

## Datos

En el análisis se encuentran 735 programas diferentes. Hay algunos errores menores por lo que no estaríá de más un _refine_.  
Existen tambien datos de los capítulos específicos de cada programa, por ejemplo para _Encuentro en el estudio_ se podrían especificar los artistas que fueron y las repeticiones de cada uno.  

Los resultados [fueron ponderados segun día y hora](https://github.com/avdata99/ScrapEncuentro/blob/master/scrapencuentro.py#L76-L104) (con criterio discrecional, casero y propio).  


Esta visualización es un ejemplo de análisis básico:  
https://plot.ly/~andresvazquez/10/
En las X está el puntaje 2016 (gestión Cambiemos), en Y el puntaje total 2013-2016 y el tamaño de cada burbuja es puntaje 2015 (gestión FPV).  

Se podrían hacer otros análisis:  
 - cantidad de programas nuevos vs repeticiones de capítulos específicos.
 - cantidad de novedad vs programas viejos (incluso saber que antiguedad desde que se estrenó)
 - conocer exactamente que programas reemplazaron a otros.  