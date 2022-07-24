import pygsheets, re, datetime, os
import pandas as pd
import dateutil.relativedelta as REL


class Gsheet:
    def __init__(self) -> None:
        self.df = None
        self.gc = pygsheets.authorize(service_file='./key.json')
        self.sht = self.gc.open_by_url('https://docs.google.com/spreadsheets/d/1dNyzXX57Ii2hLvWYZMWwDL34TBhS-XBVrX1VBaGzNas/edit#gid=1214694842')
    
    def init_all(self):
        #選取by順序
        self.wks = self.sht[0]

        start_col = 2
        start_row = 5

        #讀取
        title = self.wks.cell('A1').value
        print(title)
        self.year = title[0:4]
        services = self.wks.get_col(1, include_tailing_empty=False)
        services = services[4:17]

        dates = self.wks.get_row(4)[1:]
        dates = [x for x in dates if x != '']
        real_date = []
        for d in dates:
            matched = re.match(r'([\d]*).([\d]*).', d)
            if matched:
                self.m = matched.group(1).rjust(2,'0')
                self.d = matched.group(2).rjust(2,'0')
                real_date.append(f'{self.year}-{self.m}-{self.d}')

        people_matrix = self.wks.get_values((5,2), (17,start_col+len(real_date)))
        df = pd.DataFrame(people_matrix)
        df.iterrows()

        all_records = []
        for c, day in enumerate(real_date):
            for r, service in enumerate(services):
                clean_name = "".join([x for x in df.at[r, c] if x != " "])
                clean_service = "".join([x for x in service if x != " "])
                people = {'date': day, 'name': clean_name, 'service': clean_service}
                all_records.append(people)

        self.dfAll = pd.DataFrame(all_records)
        return self.dfAll
    
    def distict_input_cat(self, input_txt):
        matched = re.match(r'([\d]{4})*[-\/\\\.\s]*([\d]{1,2})[-\/\\\.\s]([\d]{1,2})', input_txt)
        print(f"matched date?: {matched}")
        input_type = 'name'
        value = input_txt
        if matched:
            input_type = 'date'
            cats = len(matched.groups())
            print(matched.groups())
            print(f"len of group: {cats}")
            if cats == 3:
                y = datetime.datetime.today().date().year
                if matched.group(1):
                    y = matched.group(1).rjust(4,'0')
                m = matched.group(2).rjust(2,'0')
                d = matched.group(3).rjust(2,'0')
                print(f"found date: {y}-{m}-{d}")
                value = f"{y}-{m}-{d}"
        elif input_txt in ['下週', '本週', '下周', '本周']:
            today = datetime.date.today()
            rd = REL.relativedelta(days=1, weekday=REL.SU)
            next_sunday = today + rd
            y = f"{next_sunday.year}".rjust(4,'0')
            m = f"{next_sunday.month}".rjust(2,'0')
            d = f"{next_sunday.day}".rjust(2,'0')
            value = f"{y}-{m}-{d}"
            return 'date', value
        return input_type, value

    def get_all_people_by_date(self,date):
        try:
            df_name = self.dfAll.loc[self.dfAll['date'].str.contains(date, regex=False)]
            return df_name
        except Exception as e:
            print(e)
            return None
    
    def get_by_name(self,name):
        try:
            df_name = self.dfAll.loc[self.dfAll['name'].str.contains(name, regex=False)]
            return df_name
        except Exception as e:
            print(e)
            return None
    
    def fmt_useful_message(self, df, type= 'name'):
        data = df.to_dict('records')
        future_data = []
        for r in data:
            y = int(r['date'][0:4])
            m = int(r['date'][5:7])
            d = int(r['date'][8:])
            this_date = datetime.datetime(year=y, month=m, day=d)
            if datetime.datetime.today().date() < this_date.date():
                future_data.append(r)
        if len(future_data) == 0:
            return '找不到接下來的服事資訊喔！'
        fmt_str = f'''哈囉，可能的服事如下列資訊:\r\n'''
        for r in future_data:
            y = int(r['date'][0:4])
            m = int(r['date'][5:7])
            d = int(r['date'][8:])
            this_date = datetime.datetime(year=y, month=m, day=d)
            if datetime.datetime.today().date() < this_date.date():
                if type == 'date':
                    row = f"{r['service']}: {r['name']}\r\n"
                else:
                    row = f"{r['date']}\r\n{r['service']}: {r['name']}\r\n"

                fmt_str += row
        return fmt_str
    
    def smart_query(self, input_txt):
        input_type, value = gs.distict_input_cat(input_txt)
        df = None
        if input_type == 'name':
            df = gs.get_by_name(value)
        elif input_type == 'date':
            df = gs.get_all_people_by_date(value)
        return df, input_type

gs = Gsheet()
gs.init_all()

def test():
    df, input_type = gs.smart_query('4 17')
    ret = gs.fmt_useful_message(df, input_type)
    print(ret)

if __name__=='__main__':
    test()
