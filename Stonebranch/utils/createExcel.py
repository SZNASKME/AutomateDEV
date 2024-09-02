import pandas as pd

def createExcel(outputfile, *data):
    try:
        with pd.ExcelWriter(outputfile) as writer:
            for df, sheetname in data:
                df.to_excel(writer, sheet_name=sheetname, index=False)
        print("File created successfully")
    except Exception as e:
        print(f"Error creating {outputfile}: {e}")