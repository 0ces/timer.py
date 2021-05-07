import argparse
from os import chdir
from os.path import exists, join
import sqlite3
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
import pathlib
from time import sleep
from subprocess import Popen, PIPE

class Task(object):
    def __init__(self, connection, cursor, task):
        self.__connection = connection
        self.__cursor = cursor
        self.__task = task
        self.__process = None
        self.__task['running'] = False
    
    def insert(self):
        print(self.__task)
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
    
    def update(self):
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
                self.__task['path'],
                self.__task['hora'],
                self.__task['minuto'],
                self.__task['dia'],
                self.__task['mes'],
                self.__task['ano'],
                self.__task['id']
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
        self.__task['running'] = self.__process and self.__process.poll() != None
    
    def must_run(self, now):
        if self.compare(now.year, self.__task['ano']):
            if self.compare(now.month, self.__task['mes']):
                if self.compare(now.strftime('%a'), self.__task['dia']) or self.compare(now.strftime('%A'), self.__task['dia']) or self.compare(now.day, self.__task['dia']):
                    if self.compare(now.hour, self.__task['hora']):
                        if self.compare(now.minute, self.__task['minuto']):
                            return True
        return False

    def compare(at1, at2):
        return at1 == at2 or at2 == '*'

class Main(object):
    def __init__(self):
        self.console = Console()
        self.__current_path = pathlib.Path(__file__).parent.absolute()
        self.__DB_PATH = join(self.__current_path, 'timer.db')
        chdir(self.__current_path)
        base_initted = self.get_if_database()
        self.con = sqlite3.connect(self.__DB_PATH)
        self.cur = self.con.cursor()
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
        elif self.args.show_tasks:
            self.console.print(self.get_task_table(self.tasks))
        elif self.args.delete_task:
            self.console.print(self.get_task_table(self.tasks))
            delete_id = input('Ingrese el id a eliminar: ')
            for task in self.tasks:
                if f"{task.get_task()['id']}" == delete_id:
                    task.delete()
        elif self.args.edit_task:
            pass
        else:
            pass
    
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


if __name__ == '__main__':
    Main()