# **timer.py**
Un script para la ejecución automática de comandos dado un tiempo específico.

 # Contenido
 - [Instalación](#instalacion)
 - [Uso](#usage)

# <a name="instalacion"></a> Instalación

Esta instalación está pensada principalmente para sistemas *Linux*.

Para instalarlo es tan sencillo como clonar este repositorio con:

```shell
$ git clone https://github.com/0ces/timer.py.git
```


Instalar los requisitos con:

```shell
$ pip3 install -r src/requirements.txt
```

Ejecutar el proceso principal con:

```shell
$ python3 src/timer.py
```

Si quieres que se ejecute automáticamente puedes añadir un comando a la hora de iniciar tu sistema operativo como el siguiente:

```shell
$ python3 /path/to/repo/timer.py/src/timer.py
```


# <a name="usage"></a> Uso
Para conocer los diferentes argumentos con los que se puede ejecutar el script ejecute:

```shell
$ python3 src/timer.py -h
usage: timer.py [-h] [-a] [-s] [-d] [-e]

optional arguments:
  -h, --help         show this help message and exit
  -a, --add-task
  -s, --show-tasks
  -d, --delete-task
  -e, --edit-task
```


## Añadir tareas:
```shell
$ python3 src/timer.py -a
```
A la hora de añadir tareas se te pedirá la siguiente información:
1. El comando a ejecutar.
2. La hora.
3. El minuto.
4. El día que se va a ejecutar, este puede ser el día especifico del mes (e.g. 24) o un día de la semana, para esto debes especificar el día en inglés, ya sea su abreviatura o el nombre completo.

<center>

| Día         | Day         | Abbreviation |
| ----------- | ----------- | ------------ |
| Domingo     | Sunday      | Sun          |
| Lunes       | Monday      | Mon          |
| Martes      | Tuesday     | Tue          |
| Miércoles   | Wednesday   | Wed          |
| Jueves      | Thursday    | Thu          |
| Viernes     | Friday      | Fri          |
| Sábado      | Saturday    | Sat          |

</center>

5. El mes.
6. El año.

Una vez completada esta información se añadirá a la base de datos.

## Listar tareas:
```shell
$ python src/timer.py -s
```

Nos mostrará una tabla como la siguiente donde podremos ver las tareas que tenemos programadas:

<center>

| id | command                  | hora | minuto | dia | mes | año | running |
| :-: | ----------------------- | :--: | :----: | :-: | :-: | :-: | :------ |
| 1  | `python3 example.py`     | *    | *      | Mon | *   | *   | False   |
| 2  | `restart`                | 21   | 0      | *   | *   | *   | False   |

</center>

## Eliminar tareas:
```shell
$ python src/timer.py -d
```
Ejecutando este parametro se nos mostrará la tabla de tareas programadas y se nos pedirá el id de la tarea que deseamos eliminar.

## Editar tareas:
```shell
$ python src/timer.py -e
```
Ejecutando este parametro se nos mostrara la tabla de tareas programadas y se nos pedirá el id de la tarea que deseamos editar, una vez ingresado el id se hará un proceso parecido al de añadir tareas pero en caso de que se desee conservar el valor actual solo hay que presionar enter sin ingresar nada.

