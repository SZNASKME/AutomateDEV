import processGetData as pgd
import processCompareData as pcd


SHEET_NAME = "Sheet"
EXCEL_COMPARE_COLUMN = 'jobName'
API_COMPARE_COLUMN = 'name'
OUTPUT_FILE = 'Excel_API_Difference.xlsx'


LIST_TASK_URI = "http://172.16.1.85:8080/uc/resources/task/list"
LIST_TASK_ADV_URI = "http://172.16.1.85:8080/uc/resources/task/listadv"

task_configs = {
    'name': '*',
    'type':  'Universal',
}

task_adv_configs = {
    'taskname': '*',
    'type': 'Timer',
    'updatedTime': '-5d',
}

auth = ('ops.admin','p@ssw0rd')


def main():
    Exceldata = pgd.getDataExcel()
    conti = input("Do you want to get API data / next to compare API data w/ Excel data? [y/n]: ")
    if conti.lower() != 'y':
        return
    APIdata = pgd.getDataAPI()

    CompareExcel = pcd.compareDataExcelAPI(Exceldata, APIdata, api_compare_column = API_COMPARE_COLUMN, compare_column = EXCEL_COMPARE_COLUMN)
    #print(CompareExcel)
    pcd.createExcel(CompareExcel, OUTPUT_FILE)




if __name__ == "__main__":
    main()