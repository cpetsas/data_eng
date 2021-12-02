import pandas
import networkx
from matplotlib.pyplot import figure
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class NetworkCreator:

    def __init__(self, tasks_path, dependencies_path, resources_path):
        self.tasks_path = tasks_path
        self.dependencies_path = dependencies_path
        self.resources_path = resources_path
        self.generated_files = []

    def generate_everything(self):
        self.create_resoucesDF()
        self.create_dependenciesDF()
        self.create_tasksDF()
        self.create_network_taskResourceAmount_on_each_Task()
        self.create_task_network()
        self.generate_statistics_difference_between_task_time()

    def clean_taskDF(self, df):
        df = df[df.columns.drop(list(df.filter(regex='Unnamed')))]
        df = df[pandas.to_numeric(df['task_id'], errors='coerce').notnull()]
        df = df[pandas.to_numeric(df['target_duration'], errors='coerce').notnull()]
        df = df[pandas.to_numeric(df['actual_duration'], errors='coerce').notnull()]
        df = df[pandas.to_numeric(df['r'], errors='coerce').notnull()]
        df = df[pandas.to_datetime(df['target_start_date'], errors='coerce').notnull()]
        df = df[pandas.to_datetime(df['target_end_date'], errors='coerce').notnull()]
        return(df)

    def clean_resourcesDF(self, df):
        df = df[pandas.to_numeric(df['taskrsrc_id'], errors='coerce').notnull()]
        df = df[pandas.to_numeric(df['task_id'], errors='coerce').notnull()]
        df['role_id'] = pandas.to_numeric(df['role_id'], errors='coerce').fillna(0)
        return(df)

    def clean_dependenciesDF(self, df):
        df = df[pandas.to_numeric(df['pred_task_id'], errors='coerce').notnull()]
        df = df[pandas.to_numeric(df['task_id'], errors='coerce').notnull()]
        return(df)

    def create_resoucesDF(self):
        resource_df = pandas.read_csv(self.resources_path)
        self.resource_df = self.clean_resourcesDF(resource_df)

    def create_dependenciesDF(self):
        dependencies_df = pandas.read_csv(self.dependencies_path)
        self.dependencies_df = self.clean_dependenciesDF(dependencies_df)

    def create_tasksDF(self):
        task_df = pandas.read_csv(self.tasks_path)
        self.task_df = self.clean_taskDF(task_df)

    def create_task_network(self):
        nonFailedTasks = self.task_df.loc[(self.task_df['target_duration'] > 0) & (self.task_df['actual_duration'] > 0)]
        df = nonFailedTasks.merge(self.dependencies_df, on='task_id')
        graph = networkx.Graph()
        graph = networkx.from_pandas_edgelist(df, 'task_id', 'pred_task_id')
        networkx.draw(graph, with_labels=True)
        self.handle_graph(representation = 'graph')

    def create_network_taskResourceAmount_on_each_Task(self):
        df = self.resource_df.groupby(by='task_id',as_index=False).agg({'taskrsrc_id': pandas.Series.nunique})
        df = df.loc[df['taskrsrc_id'] > 30]
        x = df.task_id.astype(str)
        y = df['taskrsrc_id']
        fig = plt.figure()
        fig.suptitle('Number of employees on each task', fontsize=20)
        plt.bar(x,y)
        plt.xticks(rotation = 60)
        self.handle_graph(representation='figure')
    
    def generate_statistics_difference_between_task_time(self):
        actualTasks = self.task_df.loc[(self.task_df['target_duration'] > 0) & (self.task_df['actual_duration'] > 0)]
        df = actualTasks.groupby(by='r', as_index=True).agg({'task_id': pandas.Series.nunique})
        df.plot(kind='pie', y='task_id', autopct='%1.1f%%', title='Task amount against r (delay amount)')
        self.handle_graph()

    def handle_graph(self, representation = 'figure'):
        timestamp = datetime.now()
        timestamp = str(timestamp.timestamp())
        timestamp = timestamp.replace('.','_')
        file_name = 'reports/'+ timestamp + '.png'
        plt.savefig(file_name, dpi =800)
        plt.clf()
        self.generated_files.append(file_name)


if __name__ == "__main__":
    creator = NetworkCreator("Tasks.csv", "Task_dependencies.csv", "resource_assignment.csv")
    creator.create_resoucesDF()
    creator.create_dependenciesDF()
    creator.create_tasksDF()
    creator.create_network_taskResourceAmount_on_each_Task()
    creator.create_task_network()
    creator.generate_statistics_difference_between_task_time()
