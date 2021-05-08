#!/usr/bin/env python3

import argparse
from os import chdir
from os.path import exists, join, getmtime
import sqlite3
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.live import Live
import pathlib
from time import sleep, time
from subprocess import Popen, PIPE
from datetime import datetime
from notifypy import Notify

class Task(object):
    def __init__(self, connection, cursor, task):
        self.__connection = connection
        self.__cursor = cursor
        self.__task = task
        self.__process = None
        self.__task['running'] = False
    
    def insert(self):
        self.__cursor.execute("""
        INSERT INTO tasks VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """, [
                self.__task['path'],
                self.__task['hora'],
                self.__task['minuto'],
                self.__task['dia'],
                self.__task['mes'],
                self.__task['ano']
        ])
        self.__connection.commit()
    
    def update(self, new_task):
        self.__cursor.execute("""
        UPDATE tasks
        SET
        path = ?,
        hora = ?,
        minuto = ?,
        dia = ?,
        mes = ?,
        ano = ?
        WHERE
        rowid = ?
        """, [
                new_task['path'],
                new_task['hora'],
                new_task['minuto'],
                new_task['dia'],
                new_task['mes'],
                new_task['ano'],
                new_task['id']
        ])
        self.__connection.commit()
    
    def delete(self):
        self.__cursor.execute("""
        DELETE FROM tasks WHERE rowid = ?
        """, [self.__task['id']])
        self.__connection.commit()
    
    def get_task(self):
        self.get_if_running()
        return self.__task
    
    def run(self):
        self.__process = Popen(self.__task['path'].split())
        self.__task['running'] = True
    
    def get_if_running(self):
        self.__task['running'] = bool(self.__process and self.__process.poll() != None)
    
    def must_run(self, now):
        if self.compare(now.year, self.__task['ano']):
            if self.compare(now.month, self.__task['mes']):
                if self.compare(now.strftime('%a'), self.__task['dia']) or self.compare(now.strftime('%A'), self.__task['dia']) or self.compare(now.day, self.__task['dia']):
                    if self.compare(now.hour, self.__task['hora']):
                        if self.compare(now.minute, self.__task['minuto']):
                            return True
        return False

    def compare(self, at1, at2):
        return str(at1) == str(at2) or str(at2) == '*'

class Main(object):
    def __init__(self):
        self.notification = Notify(
            default_notification_title='Timer'
        )
        self.console = Console()
        self.__current_path = pathlib.Path(__file__).parent.absolute()
        self.__DB_PATH = join(self.__current_path, 'timer.db')
        chdir(self.__current_path)
        base_initted = self.get_if_database()
        self.startDB()
        if not base_initted:
            self.cur.execute("""
            CREATE TABLE tasks(
                path text,
                hora text,
                minuto text,
                dia text,
                mes text,
                ano text
            );
            """)
            self.con.commit()
        self.args = self.get_args()
        self.tasks = self.get_tasks_objs(self.get_tasks())
        if self.args.add_task:
            task = {}
            task['path'] = input('Ingrese el comando a ejecutar: ')
            task['hora'] = input('Ingrese la hora (0-23, *): ')
            task['minuto'] = input('Ingrese el minuto (0-60, *): ')
            task['dia'] = input('Ingrese el dia (Mon-Sun, 1-31, *): ')
            task['mes'] = input('Ingrese el mes (1-12, *): ')
            task['ano'] = input('Ingrese el año (NNNN, *): ')
            Task(self.con, self.cur, task).insert()
            self.send_noti(f'Se ha agregado una nueva tarea\nTareas totales: {len(self.tasks)+1}')
        elif self.args.show_tasks:
            self.console.print(self.get_task_table(self.tasks))
        elif self.args.delete_task:
            self.console.print(self.get_task_table(self.tasks))
            delete_id = input('Ingrese el id a eliminar: ')
            for task in self.tasks:
                if f"{task.get_task()['id']}" == delete_id:
                    task.delete()
                    self.send_noti(f'Se ha eliminado una tarea\nTareas totales: {len(self.tasks)-1}')
        elif self.args.edit_task:
            self.console.print(self.get_task_table(self.tasks))
            edit_id = input('Ingrese el id a editar: ')
            for taskObj in self.tasks:
                task = taskObj.get_task()
                if f"{task['id']}" == edit_id:
                    new_task = {
                        'id': task['id']
                    }
                    new_task['path'] = input(f'Ingrese el comando a ejecutar [{task["path"]}]: ') or task['path']
                    new_task['hora'] = input(f'Ingrese la hora (0-23, *) [{task["hora"]}]: ') or task['hora']
                    new_task['minuto'] = input(f'Ingrese el minuto (0-60, *) [{task["minuto"]}]: ') or task['minuto']
                    new_task['dia'] = input(f'Ingrese el dia (Mon-Sun, 1-31, *) [{task["dia"]}]: ') or task['dia']
                    new_task['mes'] = input(f'Ingrese el mes (1-12, *) [{task["mes"]}]: ') or task['mes']
                    new_task['ano'] = input(f'Ingrese el año (NNNN, *) [{task["ano"]}]: ') or task['ano']
                    taskObj.update(new_task)
                    self.send_noti(f'Se ha modificado una tarea\nTareas totales: {len(self.tasks)}')
        else:
            self.send_noti(f'¡Timer ha iniciado!\nTareas totales: {len(self.tasks)}')
            with Live(self.get_task_table(self.tasks), refresh_per_second=4) as live:
                while True:
                    if getmtime(self.__DB_PATH) > self.lastdbmod:
                        self.startDB()
                    self.tasks = self.get_tasks_objs(self.get_tasks())
                    now = datetime.now()
                    for task in self.tasks:
                        if task.must_run(now):
                            task.run()
                            self.send_noti(f'Ejecutando tarea con id {task.get_task()["id"]}.')
                    live.update(self.get_task_table(self.tasks))
                    sleep(60 - now.second)
    
    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--add-task', action='store_true')
        parser.add_argument('-s', '--show-tasks', action='store_true')
        parser.add_argument('-d', '--delete-task', action='store_true')
        parser.add_argument('-e', '--edit-task', action='store_true')
        return parser.parse_args()
    
    def get_if_database(self):
        return exists(self.__DB_PATH)
    
    def get_tasks(self):
        self.cur.execute("""
        SELECT rowid, * FROM tasks;
        """)
        results = self.cur.fetchall()
        tasks = []
        for task in results:
            tasks.append({
                'id': task[0],
                'path': task[1],
                'hora': task[2],
                'minuto': task[3],
                'dia': task[4],
                'mes': task[5],
                'ano': task[6]
            })
        return tasks

    def get_tasks_objs(self, tasks):
        tasks_objs = []
        for task in tasks:
            tasks_objs.append(Task(self.con, self.cur, task))
        return tasks_objs

    def get_task_table(self, tasks):
        table = Table(
            'id',
            'path',
            'hora',
            'minuto',
            'dia',
            'mes',
            'año',
            'running',
            title='Tasks'
        )

        for taskObj in tasks:
            task = taskObj.get_task()
            table.add_row(
                f"{task['id']}",
                task['path'],
                task['hora'],
                task['minuto'],
                task['dia'],
                task['mes'],
                task['ano'],
                f"[green]{task['running']}[/green]" if task['running'] else f"[red]{task['running']}[/red]"
            )

        return table
    
    def startDB(self):
        self.con = sqlite3.connect(self.__DB_PATH)
        self.lastdbmod = getmtime(self.__DB_PATH)
        self.cur = self.con.cursor()
    
    def send_noti(self, msg):
        self.notification.message = msg
        self.notification.send(block=False)


if __name__ == '__main__':
    Main()