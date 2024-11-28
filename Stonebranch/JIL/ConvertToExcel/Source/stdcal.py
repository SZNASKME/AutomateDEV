import pandas as pd
from datetime import datetime

def parse_data(lines):
    data = []
    current_entry = {}

    for line in lines:
        line = line.strip()

        if line.startswith("calendar:"):
            if current_entry:
                data.append(current_entry)
            current_entry = {'calendar': line.split(":")[1].strip()}
        else:
            date_str = line.replace(' 00:00', '')
            date_object = datetime.strptime(date_str, '%m/%d/%Y')
            
            if date_object.year >= 2022:
                current_entry.setdefault(f'Year_{date_object.year}', []).append(date_str)

    if current_entry:
        data.append(current_entry)

    return data

def write_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    # Replace 'input.txt' with the actual path to your text file
    input_file_path = "D:\Developer\Python\JIL-To-Excel-master\\NOV25_2024\\stdcal.txt"
    # Replace 'output.xlsx' with your desired output file name
    output_file_path = "D:\Developer\Python\JIL-To-Excel-master\\NOV25_2024\\NOV25_2024_stdcal.xlsx"

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    parsed_data = parse_data(lines)
    write_to_excel(parsed_data, output_file_path)

    print(f"Conversion completed. Excel file saved at: {output_file_path}")
