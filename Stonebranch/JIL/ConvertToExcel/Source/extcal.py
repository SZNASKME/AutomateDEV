import pandas as pd

def parse_data(lines):
    data = []
    current_entry = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        key, value = line.split(':')
        key = key.strip()
        value = value.strip()

        if key == 'extended_calendar':
            if current_entry:
                data.append(current_entry)
            current_entry = {'extended_calendar': value}
        else:
            current_entry[key] = value

    if current_entry:
        data.append(current_entry)

    return data

def write_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    # Replace 'input.txt' with the actual path to your text file
    # input_file_path = "D:\Developer\Python\Autosys\extcal_2024.txt"
    input_file_path = "D:\Developer\Python\JIL-To-Excel-master\\NOV25_2024\\extcal.txt"
    # D:\AskMe\OneDrive - AskMe Solutions & Consultants Co., Ltd\Customer Projects\TTB - Stonebranch\Implement\DATA From TTB\Autosys JIL\09 CH24-0013679_autosys_output
    # Replace 'output.xlsx' with your desired output file name
    output_file_path = "D:\Developer\Python\JIL-To-Excel-master\\NOV25_2024\\NOV25_2024_extcal.xlsx"

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    parsed_data = parse_data(lines)
    write_to_excel(parsed_data, output_file_path)

    print(f"Conversion completed. Excel file saved at: {output_file_path}")
