import luigi
from datetime import date, timedelta


class ProcessDataTask(luigi.Task):
    # 添加一个date参数
    date = luigi.DateParameter()

    def output(self):
        # 输出目标是基于日期的文件
        return luigi.LocalTarget(self.date.strftime('data_%Y-%m-%d.txt'))

    def run(self):
        # 模拟处理特定日期的数据
        with self.output().open('w') as f:
            f.write(f"Data for {self.date}\n")


class AggregateDataTask(luigi.Task):
    start_date = luigi.DateParameter()
    end_date = luigi.DateParameter()

    def requires(self):
        # 生成从start_date到end_date的所有ProcessDataTask实例
        current_date = self.start_date
        while current_date <= self.end_date:
            yield ProcessDataTask(date=current_date)
            current_date += timedelta(days=1)

    def output(self):
        # 聚合后的输出文件
        return luigi.LocalTarget('aggregated_data.txt')

    def run(self):
        # 读取所有输入并聚合
        with self.output().open('w') as fout:
            for input in self.input():
                with input.open() as fin:
                    for line in fin:
                        fout.write(line)


if __name__ == '__main__':
    # 指定开始和结束日期
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 5)

    # 运行AggregateDataTask，它会触发多个ProcessDataTask实例
    luigi.run(
        ['--local-scheduler', '--workers', '4', 'AggregateDataTask', '--start-date', str(start_date), '--end-date',
         str(end_date)])
