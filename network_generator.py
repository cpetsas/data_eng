import pandas
import networkx
from matplotlib.pyplot import figure

class NetworkCreator:

    def __init__(self, tasks_path, dependencies_path, resources_path):
        self.tasks_path = tasks_path
        self.dependencies_path = dependencies_path
        self.resources_path = resources_path

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

    def create_resoucesDF(self):
        resource_df = pandas.read_csv(self.resources_path)
        # print(resource_df)
        self.resource_df = self.clean_resourcesDF(resource_df)
        # print(resource_df)


    def create_tasksDF(self):
        task_df = pandas.read_csv(self.tasks_path)
        self.task_df = self.clean_taskDF(task_df)
        # self.create_tasks_network(self.task_df)

    def create_tasks_network(self, df):
        df = df.loc[(df['target_duration'] > 0) & (df['actual_duration'] == 0)]
        print(df)

    def create_network_taskResourceAmount_on_each_Task(self):
        df = self.resource_df.groupby(by='task_id',as_index=False).agg({'taskrsrc_id': pandas.Series.nunique})
        graph = networkx.Graph()
        graph = networkx.from_pandas_edgelist(df, 'task_id', 'taskrsrc_id')
        figure(figsize=(15,15))
        networkx.draw_shell(graph, with_labels=True)
        print(df)



if __name__ == "__main__":
    creator = NetworkCreator("Tasks.csv", "Task_dependencies.csv", "resource_assignment.csv")
    creator.create_resoucesDF()
    creator.create_network_taskResourceAmount_on_each_Task()