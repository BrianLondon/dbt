import dbt.project as project

class HostedTask:
    def __init__(self, args, project):
        self.args = args
        self.project = project

    def run(self):
        print "running hosted!!"
