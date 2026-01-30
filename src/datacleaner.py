from dependencies import Dependencies as dp
class DataCleaner:
    pd=dp.get_pandas()

    @staticmethod
    def loader(file_path):
        origin_data=pd.read_csv(file_path)
        df.fillna(method="ffill")#Need to change method if necessary
        df.groupby().agg()
        pd.merge()
