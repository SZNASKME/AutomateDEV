import sys
import os
import re
import pandas as pd
import json
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
CONDITION_COLUMN = 'condition'

JOB_COLUMN_OUTPUT = 'jobName'
BOX_COLUMN_OUTPUT = 'box_name'
FIRST_OPERAND_COLUMN_OUTPUT = 'firstOperand'
SECOND_OPERAND_COLUMN_OUTPUT = 'secondOperand'
OPERATOR_COLUMN_OUTPUT = 'operator'
CONDITION_COLUMN_OUTPUT = 'condition'



# Daily and Monthly format condition
FORMAT_CONDITION = [
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
        "subOperand": ["D.", "M."]
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

left_operator_format = ['(']
right_operator_format = [')']

pattern = r'([()&|])|(\w+\([^)]+\))'

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

def checkFormatOperator(string, format_condition):
    for condition_data in format_condition:
        if string in condition_data['operator']:
            return True
    return False

def findComplexConditionIndex(str, sub_str_list):
    for index in range(0, len(sub_str_list)):
        if sub_str_list[index] in str:
            return index

def checkFormatOperandCommon(first_operand, second_operand, format_condition):
    for condition_data in format_condition:
        first_operand_index = findComplexConditionIndex(first_operand, condition_data['subOperand'])
        second_operand_index = findComplexConditionIndex(second_operand, condition_data['subOperand'])
        if (first_operand_index != None and second_operand_index != None
            and first_operand_index != second_operand_index):
            return True
    return False

def findOperands(filtered_string, operator_index, direction = 'left'):
    sub_string_list = []
    if direction == 'left':
        slice_index = operator_index - 1
        while slice_index >= 0:
            current_sub_string = filtered_string[slice_index]
            if current_sub_string in left_operator_format:
                break
            if re.match(operand_pattern, current_sub_string):
                sub_string_list.append(current_sub_string)
            slice_index -= 1
    
    elif direction == 'right':
        index = operator_index + 1
        while index < len(filtered_string):
            current_sub_string = filtered_string[index]
            if current_sub_string in right_operator_format:
                break
            if re.match(operand_pattern, current_sub_string):
                sub_string_list.append(current_sub_string)
            index += 1
            
    return sub_string_list
        

def compareCondition(df_jil, format_condition, in_list_condition):
    found_format_condition = []
    for index, row in df_jil.iterrows():
        if row[JOBNAME_COLUMN] in in_list_condition:
            continue
        condition = row[CONDITION_COLUMN]
        if not isinstance(condition,str) or (isinstance(condition,float) and math.isnan(condition)):
            continue
        separate_string = re.findall(pattern, condition)
        filtered_string = [item for sublist in separate_string for item in sublist if item]
        
        for index in range(0, len(filtered_string)):
            operator_sub_string = filtered_string[index]
            if checkFormatOperator(operator_sub_string, format_condition):
                #print(filtered_string)
                left_sub_string_list = findOperands(filtered_string, index, 'left')
                right_sub_string_list = findOperands(filtered_string, index, 'right')
                for left_sub_string in left_sub_string_list:
                    for right_sub_string in right_sub_string_list:
                        #print(left_sub_string, sub_string, right_sub_string)
                        if checkFormatOperandCommon(left_sub_string, right_sub_string, format_condition):
                            found_format_condition.append({
                                JOB_COLUMN_OUTPUT: row[JOBNAME_COLUMN],
                                BOX_COLUMN_OUTPUT: row[BOXNAME_COLUMN],
                                FIRST_OPERAND_COLUMN_OUTPUT: left_sub_string,
                                SECOND_OPERAND_COLUMN_OUTPUT: right_sub_string,
                                OPERATOR_COLUMN_OUTPUT: operator_sub_string,
                                CONDITION_COLUMN_OUTPUT: condition,
                            })
    #print(json.dumps(found_format_condition, indent=4))
    df_found_format_condition = pd.DataFrame(found_format_condition)
    return df_found_format_condition

def checkSimilarOperand(first_operand, second_operand, format_condition):
    for condition_data in format_condition:
        sub_operand = condition_data['subOperand']
        first_operand_index = findComplexConditionIndex(first_operand, sub_operand)
        second_operand_index = findComplexConditionIndex(second_operand, sub_operand)
        if first_operand_index != None and second_operand_index != None and first_operand_index != second_operand_index:
            first_operand_sub_str = sub_operand[first_operand_index]
            second_operand_sub_str = sub_operand[second_operand_index]
            break
    first_truncation_sub_str = first_operand.replace(first_operand_sub_str, '')
    second_truncation_sub_str = second_operand.replace(second_operand_sub_str, '')
    if first_truncation_sub_str == second_truncation_sub_str:
        return True
    return False

############################################################################################################

def compareSimilarOperands(df, format_condition):
    similar_condition = []
    unsimilar_condition = []
    for index, row in df.iterrows():
        first_operand = row['firstOperand']
        second_operand = row['secondOperand']
        if checkSimilarOperand(first_operand, second_operand, format_condition):
            similar_condition.append(row)
        else:
            unsimilar_condition.append(row)
    df_similar_condition = pd.DataFrame(similar_condition)
    df_unsimilar_condition = pd.DataFrame(unsimilar_condition)
    return df_similar_condition, df_unsimilar_condition

def getSpecificColumn(df, column_name):
    column_list = []
    for index, row in df.iterrows():
        column_list.append(row[column_name])
    return column_list

def getUniqueFormatCondition(df):
    df['sortedOperands'] = df.apply(lambda row: tuple(sorted([row['firstOperand'], row['secondOperand']])), axis=1)
    df_unique = df.drop_duplicates(subset=['jobName', 'sortedOperands'])
    df_unique.drop(columns=['sortedOperands'])
    
    return df_unique
    

def main():
    df_jil = getDataExcel()
    df_in_list_condition = getDataExcel("Enter the path of the excel file with the conditions to be checked")
    in_list_condition = getSpecificColumn(df_in_list_condition, 'Taskname')
    df_format_condition = compareCondition(df_jil, FORMAT_CONDITION, in_list_condition)
    df_unique_format_condition = getUniqueFormatCondition(df_format_condition)
    df_similar_condition, df_unsimilar_condition = compareSimilarOperands(df_unique_format_condition, FORMAT_CONDITION)
    createExcel("DAILY_OR_MONTHLY_condition.xlsx", ('Similar Pair', df_similar_condition), ('Unsimilar Pair', df_unsimilar_condition))
    
if __name__ == '__main__':
    main()