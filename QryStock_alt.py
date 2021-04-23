from datetime import datetime
import sys, os, time
from PySimpleGUI.PySimpleGUI import Input
from selenium import webdriver
import selenium
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
import csv
import pathlib
import os
from pandas import DataFrame
import PySimpleGUI as sg

class PyGui:
    TableList=''
    TableListHeading=''
    def __init__(self) -> None:
        pass
    def open_Table(self,Qry):
        tableDF = DataFrame()
        tableDF = Qry.crawlDataDF
        self.TableList = tableDF.values.tolist()
        self.TableListHeading = list(tableDF.head())
        return self.set_Table_Window()
    def set_Table_Window(self):
        Table_Window_Layout=[
            [sg.Table(self.TableList,headings=self.TableListHeading,num_rows=min(30,len(self.TableList)),k='Table', select_mode="extended", def_col_width=20, vertical_scroll_only=False, auto_size_columns=False)],
            [sg.Text('排序條件\t'),sg.Combo(self.TableListHeading,default_value=self.TableListHeading[0],enable_events=True,size=(20,1),k='-Sort-',readonly=True),sg.Radio('由大到小','sort',default=True,k='SortFromMax',enable_events=True),sg.Radio('由小到大','sort',k='SortFromMin',enable_events=True)],
            [sg.Button('匯出'),sg.Button('關閉'),sg.Button('重新爬取')]
        ]
        return sg.Window('結果清單',Table_Window_Layout,margins=(5,5),finalize=True,resizable=False)
    def set_StartUp_Window(self,Qry):
        startUp_Window_Layout=[
            [sg.Text('輸入年份（民國）'),sg.Input(k='-Year-',size=(6,1)),sg.Text('輸入月份'),sg.Input(k='-Month-',size=(4,1))],
            [sg.Button('確定'),sg.Button('取消')]
        ]
        return sg.Window('選擇時間點',startUp_Window_Layout,margins=(10,5), finalize=True)

class QryStock:
    inputCoid_Element = ''
    sub_Coid_Element =''
    current_Date_Index =''
    current_Year =''
    current_Month = ''
    year_Element =''
    month_Element =''
    driver=''
    coidList=[]
    no_exist_List=[]
    current_coid=''
    dateList=[]
    crawlDataDF=[]
    current_Process=0
    total=0
    exist=0
    import_csv='.\上市&上櫃.csv'
    coidList_Dict={"股號":[],"股名":[],"千張持股變化":[],"抓取週千張持股":[],"抓取週之上週千張持股":[]}
    coidList_Dict_Type={"股號":'string',"股名":'string',"千張持股變化":'double',"抓取週千張持股":'double',"抓取週之上週千張持股":'double'}

    def update_TableData(self):
        Pygui.TableList=self.crawlDataDF.values.tolist()
        Pygui.TableListHeading=list(self.crawlDataDF.head())
        table_Window['Table'].update(values=Pygui.TableList,num_rows=min(30,len(Pygui.TableList)))
        pass
    def sort(self,sortString,isFromMin):
        self.crawlDataDF = self.crawlDataDF.sort_values(by=sortString,ascending=isFromMin,axis=0)
        self.update_TableData()
        pass
    def export(self):
        filename = sg.popup_get_file('選擇儲存路徑','匯出表格',default_path=f'{self.current_Year}-{self.current_Month} - 董監事持股餘額明細資料 － 匯出',save_as=True,file_types=(("CSV 檔","*.csv"),("Excel 檔","*.xlsx")),no_window=True)
        if(pathlib.Path(filename).suffix==".csv"):
            self.crawlDataDF.to_csv(filename,encoding='utf-8', index=False)
        if(pathlib.Path(filename).suffix==".xlsx"):
            self.crawlDataDF.to_excel(filename,encoding='utf-8', index=False)
        pass
    def auto_Mode(self):  # 自動模式
        self.no_exist_List=[]
        self.coidList=[]
        self.exist=0
        filename = sg.popup_get_file('讀入股號表',no_window=True,file_types=(("CSV 股號表","*.csv"),))
        if (filename==''):
            sg.popup_error('請選擇有效的檔案名稱！')
            return False
        else:
            self.import_csv = filename
        with open(self.import_csv, newline='', encoding="utf-8") as csvfile_Lc:  # 讀入CSV檔案
            rows = csv.DictReader(csvfile_Lc)
            for row in rows:
                self.total += 1
                if((len(row['代號']) == 4) and row['代號'].isnumeric()):  # 檢查股號是否為純號碼以及是否為4位數
                    self.exist+=1
                    Co_id = row['代號']
                    name = row['名稱']
                    self.coidList.append([Co_id,name])
        return True

    def __init__(self) -> None:
        self.crawlDataDF = DataFrame(self.coidList_Dict)
        url = 'https://mops.twse.com.tw/mops/web/stapap1'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        if __name__ == "__main__":

            if getattr(sys, 'frozen', False): 
                chrome_driver_path = os.path.join(sys._MEIPASS, 'chromedriver.exe')
                print(chrome_driver_path)
                self.driver = webdriver.Chrome(executable_path=chrome_driver_path,options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
        try:
            self.driver.get(url)
        except selenium.common.exceptions.WebDriverException:
            sg.popup_error(f'建立網頁驅動器時發生問題！請檢查網路連線與網頁 {url} 的狀態！')
            os._exit(0)
        wait = ui.WebDriverWait(self.driver,10)
        wait.until(lambda driver: driver.find_element_by_id(id_='isnew'))
    
    def set_Date(self):
        pass
    
    def set_COID(self,coidData):
        wait = ui.WebDriverWait(self.driver,4)
        try:
            wait.until(lambda driver: driver.find_element_by_id(id_='isnew'))
        except selenium.common.exceptions.TimeoutException:
            self.driver.refresh()
            time.sleep(1)
            try:
                wait.until(lambda driver: driver.find_element_by_id(id_='isnew'))
            except selenium.common.exceptions.TimeoutException:
                return False
        DataType_Elemnt = Select(self.driver.find_element_by_id(id_='isnew'))
        DataType_Elemnt.select_by_index(1)
        wait.until(lambda driver: driver.find_element_by_id(id_='co_id'))
        self.inputCoid_Element = self.driver.find_element_by_id(id_='co_id')
        time.sleep(.5)
        self.inputCoid_Element.click()
        self.inputCoid_Element.send_keys(coidData[0],Keys.ENTER)
        return True

    def submit(self):
        time.sleep(3)
        self.driver.find_elements_by_xpath('/html/body/center/table/tbody/tr/td/div[4]/table/tbody/tr/td/div/table/tbody/tr/td[3]/div/div[3]/form/table/tbody/tr/td[4]/table/tbody/tr/td[2]/div/div/input')[0].click()
        wait = ui.WebDriverWait(self.driver,3)
        try:
            time.sleep(4)
            wait.until(lambda driver: driver.find_element_by_xpath('//td[contains(text(),"全體董監持股合計")]/following-sibling::td[1]'))
            table_element = self.driver.find_element_by_xpath('//td[contains(text(),"全體董監持股合計")]/following-sibling::td[1]')
            num_string = str(table_element.text)
            num = int(num_string.replace(',',''))
            print(num)
            return num
        except selenium.common.exceptions.TimeoutException:
            self.set_COID(self.current_coid)
            return None

    def submitGetlastMonth(self):
        wait = ui.WebDriverWait(self.driver,3)
        wait.until(lambda driver: driver.find_element_by_id(id_='month'))
        self.month_Element = Select(self.driver.find_element_by_name('month'))
        if(self.current_Month == 1):
            self.month_Element.select_by_index(12)
        else:
            self.month_Element.select_by_index(self.current_Month-1)
        wait.until(lambda driver: driver.find_element_by_id(id_='year'))
        self.year_Element = self.driver.find_element_by_id(id_='year')
        self.year_Element.click()
        self.year_Element.send_keys(self.current_Year,Keys.ENTER)
        pass

    def submitGetThisMonth(self):
        wait = ui.WebDriverWait(self.driver,3)
        wait.until(lambda driver: driver.find_element_by_id(id_='year'))
        self.year_Element = self.driver.find_element_by_id(id_='year')
        self.year_Element.click()
        self.year_Element.send_keys(self.current_Year,Keys.ENTER)
        wait.until(lambda driver: driver.find_element_by_id(id_='month'))
        self.month_Element = Select(self.driver.find_element_by_name('month'))
        self.month_Element.select_by_index(self.current_Month)
        pass

    def q_Sumbit_Double_Check(self):
        self.driver.refresh()
        self.current_Process=1
        local_NoExistList = self.no_exist_List
        self.no_exist_List=[]
        self.current_Date_Index=self.dateList.index(self.current_Date)
        for coid in local_NoExistList:
            currentMonth=None
            lastMonth=None
            numChange=None
            self.driver.refresh()
            self.current_coid=coid
            sg.one_line_progress_meter('爬取遺漏資料中...',self.current_Process,len(local_NoExistList),key='Process',orientation='h')
            if(self.set_COID(self.current_coid)):
                print(f'正在抓取股號：{self.current_coid}的資料')
                for i in range(1,4):
                    self.submitGetThisMonth()
                    currentMonth = self.submit()
                    if(currentMonth==None):
                        print(f'目前 {self.current_coid} 的抓取週抓取出錯第 {i} 次，重試中...')
                        self.driver.refresh()
                        time.sleep(3)
                        self.set_COID(self.current_coid)
                        continue
                    else:
                        break
                if(currentMonth==None):
                    print(f'找不到{self.current_coid}')
                    self.no_exist_List.append(self.current_coid)
                    self.current_Process+=1
                    continue
                if(self.set_COID(self.current_coid)):
                    for i in range(1,4):
                        self.submitGetlastMonth()
                        lastMonth = self.submit()
                        if(lastMonth==None):
                            print(f'目前 {self.current_coid} 的抓取週之上週抓取出錯第 {i} 次，重試中...')
                            self.driver.refresh()
                            self.set_COID(self.current_coid)
                            continue
                        else:
                            break
                    if(lastMonth==None):
                        print(f'找不到{self.current_coid}')
                        self.no_exist_List.append(self.current_coid)
                        self.current_Process+=1
                        continue
                else:
                    self.current_Process+=1
                    continue
                numChange=currentMonth-lastMonth
                dict_add={"股號":str(local_NoExistList[local_NoExistList.index(coid)][0]),"股名":str(local_NoExistList[local_NoExistList.index(coid)][1]),"抓取週":self.current_Date,"千張持股變化":numChange,"抓取週千張持股":currentMonth,"抓取週之上週千張持股":lastMonth}
                print(dict_add)
                cols=["股號","股名","抓取年月","董監持股變化","抓取月總額","抓取月之上月總額"]
                self.crawlDataDF = self.crawlDataDF.append(dict_add, ignore_index=True)
                self.crawlDataDF = self.crawlDataDF[cols]
                self.current_Process+=1
            else:
                self.current_Process+=1
                continue
    
    def q_Sumbit(self,Year,Month):
        self.crawlDataDF = DataFrame(self.coidList_Dict)
        self.current_Process=1
        self.current_Year = int(Year)
        self.current_Month = int(Month)
        for coid in self.coidList:
            currentMonth=None
            lastMonth=None
            numChange=None
            self.driver.refresh()
            self.current_coid=coid
            button = sg.one_line_progress_meter('爬取資料',self.current_Process,self.exist,key='Process',orientation='h')
            if(button == False and self.current_Process < self.exist):
                button_sub = sg.popup_yes_no('是否取消？',title='手動取消')
                if(button_sub=='Yes'):
                    return False
                else:
                    sg.one_line_progress_meter('爬取資料',self.current_Process,self.exist,key='Process',orientation='h')
            if(self.set_COID(self.current_coid)):
                print(f'正在抓取股號：{coid}的資料')
                for i in range(1,4):
                    self.submitGetThisMonth()
                    currentMonth = self.submit()
                    if(currentMonth==None):
                        print(f'目前 {coid} 的抓取月抓取出錯第 {i} 次，重試中...')
                        self.driver.refresh()
                        time.sleep(3)
                        self.set_COID(self.current_coid)
                        continue
                    else:
                        break
                if(currentMonth==None):
                    print(f'找不到{coid}')
                    self.no_exist_List.append(coid)
                    self.current_Process+=1
                    continue
                if(self.set_COID(self.current_coid)):
                    for i in range(1,4):
                        self.submitGetlastMonth()
                        lastMonth = self.submit()
                        if(lastMonth==None):
                            print(f'目前 {coid} 的抓取月之上月抓取出錯第 {i} 次，重試中...')
                            self.driver.refresh()
                            self.set_COID(self.current_coid)
                            continue
                        else:
                            break
                    if(lastMonth==None):
                        print(f'找不到{coid}')
                        self.no_exist_List.append(coid)
                        self.current_Process+=1
                        continue
                else:
                    self.current_Process+=1
                    continue
                numChange=currentMonth-lastMonth
                dict_add={"股號":str(self.coidList[self.coidList.index(coid)][0]),"股名":str(self.coidList[self.coidList.index(coid)][1]),"抓取年月":f'{self.current_Year}/{self.current_Month}',"董監持股變化":numChange,"抓取月總額":currentMonth,"抓取月之上月總額":lastMonth}
                print(dict_add)
                cols=["股號","股名","抓取年月","董監持股變化","抓取月總額","抓取月之上月總額"]
                self.crawlDataDF = self.crawlDataDF.append(dict_add, ignore_index=True)
                self.crawlDataDF = self.crawlDataDF[cols]
                self.current_Process+=1
            else:
                self.current_Process+=1
                continue
        #self.q_Sumbit_Double_Check()
        return True
        pass
Qry = QryStock()
Qry.set_Date()
Pygui = PyGui()
main_Window = Pygui.set_StartUp_Window(Qry)

def start_crawl(Year,Month):
    global table_Window,Qry,Pygui
    Month = int(Month)
    nowtime_year = datetime.today().year - 1911
    print('開始抓取',Year,'的資料')
    if( int(Year)<= nowtime_year and Month <= 12 ):
        if(Qry.auto_Mode()):
            return True
        else:
            return False
    else:
        sg.popup_error('輸入時間錯誤請重新輸入！','年份或月份錯誤')

sub_main_Window = None
table_Window = None

while True:
    window,event,values = sg.read_all_windows()
    if window == sub_main_Window:
        if event == '確定':
            if(start_crawl(values['-Year-'],values['-Month-'])):
                table_Window.close()
                sub_main_Window.close()
                if(Qry.q_Sumbit(values['-Year-'],values['-Month-'])):
                    if(len(Qry.no_exist_List)!=0):
                        print(f'以下為不存在的股號\n{Qry.no_exist_List}')
                        sg.popup_ok(f'以下為不存在的股號\n{Qry.no_exist_List}',title='不存在之股號')
                    table_Window = Pygui.open_Table(Qry)
                    Qry.sort('股號',False)
                else:
                    sub_main_Window.close()
                    table_Window = Pygui.open_Table(Qry)
        if event in ('取消',sg.WIN_CLOSED):
            sub_main_Window.close()

    if window == main_Window:
        if event == '確定':
            if(start_crawl(values['-Year-'],values['-Month-'])):
                main_Window.close()
                if(Qry.q_Sumbit(values['-Year-'],values['-Month-'])):
                    if(len(Qry.no_exist_List)!=0):
                        print(f'以下為不存在的股號\n{Qry.no_exist_List}')
                        sg.popup_ok(f'以下為不存在的股號\n{Qry.no_exist_List}',title='不存在之股號')
                    table_Window = Pygui.open_Table(Qry)
                    Qry.sort('股號',False)
                else:
                    main_Window.close()
                    break
                
        if event in ('取消',sg.WIN_CLOSED):
            break
    if window == table_Window:
        if event in('-Sort-','SortFromMax','SortFromMin'):
            Qry.sort(values['-Sort-'],values['SortFromMin'])
        if event == '匯出':
            Qry.export()
        if event in ('關閉',sg.WIN_CLOSED):
            table_Window.close()
            break
        if event == '重新爬取':
            sub_main_Window = Pygui.set_StartUp_Window(Qry)
            sub_main_Window.make_modal()
            pass

main_Window.close()
Qry.driver.quit()
#Qry.auto_Mode()
#Qry.q_Sumbit()
print(Qry.crawlDataDF)