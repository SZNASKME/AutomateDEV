import sys
import os
import re
import pandas as pd
import json
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel


format_condition = [
    {
        "operator": "|",
        "subOperand": ["_M_", "_D_"],
    },
    {
        "operator": "|",
        "subOperand": ["", "_M."],
    },
    {
        "operator": "|",
        "subOperand": ["", "_D."]
    },
    {
        "operator": "|",
        "subOperand": ["_D.", "_M."]
    },
    {
        "operator": "|",
        "subOperand": [".D.", ".M."]
    },
    {
        "operator": "|",
        "subOperand": ["_DAILY_B", "_MONTHLY_B"]
    },
    {
        "operator": "|",
        "subOperand": ["_DAILY_B", "_MTHLY_B"]
    }
]

operand_pattern = r"[a-z]\([A-Za-z0-9_\.]+\)"  # Matches operands like s(...)
operator_pattern = r"[&|()]+"              # Matches operators like &, |

operator_format = ['|', '&']

def filteredOperators(operators):
    filtered_operators = []
    separate_filtered_operators = []
    for operator in operators:
        for char in operator:
            filtered_operators.append(char)
    #print(filtered_operators)
    for index in range(0, len(filtered_operators)):
        #print(filtered_operators[index])
        if (filtered_operators[index] == '(' and filtered_operators[index+1] == ')') or (filtered_operators[index] == ')' and filtered_operators[index-1] == '('):
            continue
        separate_filtered_operators.append(filtered_operators[index])
    
    return separate_filtered_operators

def separateCondition(condition_str):
    operands = re.findall(operand_pattern, condition_str)
    operators = re.findall(operator_pattern, condition_str)
    filtered_opertors = filteredOperators(operators)
    return operands, filtered_opertors


def complexConditionIndex(str, sub_str_list):
    for index in range(0, len(sub_str_list)):
        if sub_str_list[index] in str:
            return index
        

def checkCondition(first_operand, second_operand, operator, format_condition):
    for condition_data in format_condition:
        first_operand_index = complexConditionIndex(first_operand, condition_data['subOperand'])
        second_operand_index = complexConditionIndex(second_operand, condition_data['subOperand'])
        if (first_operand_index != None and second_operand_index != None
            and first_operand_index != second_operand_index
            and condition_data['operator'] == operator):
            return True
    return False

def compareCondition(df_jil, format_condition):
    found_format_condition = []
    for index, row in df_jil.iterrows():
        condition = row['condition']
        if not isinstance(condition,str) or (isinstance(condition,float) and math.isnan(condition)):
            continue
        operands, operators = separateCondition(condition)
        operator_index = 0
        for index in range(0, len(operators)):
            if operators[index] in operator_format:
                if ((index == 0) 
                    or (index >= 1 and operators[index-1] == '(' and operators[index-1] == ')')):
                    first_operand = operands[operator_index]
                    second_operand = operands[operator_index+1]
                    if checkCondition(first_operand, second_operand, operators[index], format_condition):
                        #print(row['jobName'], ":", condition)
                        #rint(f"{first_operand} {second_operand} {operators[index]}\n")
                        found_format_condition.append({
                            'jobName': row['jobName'],
                            'box_name': row['box_name'],
                            'condition': condition,
                            'firstSubOperand': first_operand,
                            'secondSubOperand': second_operand,
                            'operator': operators[index]
                        })
                operator_index += 1
    
    #print(json.dumps(found_format_condition, indent=4))
    df_found_format_condition = pd.DataFrame(found_format_condition)
    return df_found_format_condition

def main():
    df_jil = getDataExcel()
    #print(df_jil)
    df_format_condition = compareCondition(df_jil, format_condition)
    createExcel("DAILY_OR_MONTHLY_condition.xlsx", (df_format_condition, 'DAILY_OR_MONTHLY'))
    
if __name__ == '__main__':
    main()