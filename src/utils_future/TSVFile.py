from utils import File
from utils import TSVFile as TSVFileOld


class TSVFile(TSVFileOld):
    def write(self, data_list):
        TSVFileOld.write(self, data_list)

        regular_file = File(self.path)
        lines = regular_file.read_lines()
        lines = [line for line in lines if line.strip()]
        regular_file.write_lines(lines)
