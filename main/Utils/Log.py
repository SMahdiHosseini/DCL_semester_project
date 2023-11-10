
class Log:
    def __init__(self, file_name):
        self.file_name = file_name
        self.logs = ""

    def addLog(self, new_log):
        self.logs += new_log
    
    def writeLogs(self):
        file = open(self.file_name, "w")
        file.write(self.logs)
        file.close()
        