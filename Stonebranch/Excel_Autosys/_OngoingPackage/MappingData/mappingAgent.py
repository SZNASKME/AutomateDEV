import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Machine-Job Mapping.xlsx'
OUTPUT_MACHINE_SHEETNAME = 'Machine-Job Summary'
OUTPUT_MAIN_BOX_SHEETNAME = 'Main Box Summary'
OUTPUT_RESULT_SHEETNAME = 'Machine Result'
OUTPUT_SHEETNAME_LOG = 'Machine-Job Log'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'
MAINBOX_COLUMN = 'Main_Box'
MACHINE_COLUMN = 'machine'
OWNER_COLUMN = 'owner'


sys.setrecursionlimit(10000)


def findingmachineAndJob(df):
    main_box_analysis_result_list = []
    machine_analysis_result_list = []
    machine_job_result_list = []
    machine_job_log_list = []
    
    main_box_machine_dict = {}
    machine_main_box_dict = {}
    #print(df.columns)
    for row in df.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        main_box = getattr(row, MAINBOX_COLUMN)
        machine = getattr(row, MACHINE_COLUMN)
        owner = getattr(row, OWNER_COLUMN)

        if job_type == 'BOX':
            continue
        
        # Handle Self Start mainbox
        if main_box == '*Self Start' or main_box == 'Self Start':
            main_box = job_name
        
        if machine is None or pd.isna(machine) or machine == '':
            machine = 'No Machine Assigned'
        main_box_machine_dict.setdefault(main_box, {})
        main_box_machine_dict[main_box].setdefault(machine, [])
        main_box_machine_dict[main_box][machine].append((job_name, box_name, job_type, owner))
        
        machine_main_box_dict.setdefault(machine, {})
        machine_main_box_dict[machine].setdefault(main_box, [])
        machine_main_box_dict[machine][main_box].append((job_name, box_name, job_type, owner))


    for key, value in main_box_machine_dict.items():
        main_box = key
        
        main_box_analysis_result_list.append({
            'Main Box': main_box,
            'Count of Machines': len(value),
            'Total Count of Jobs': sum(len(details) for details in value.values()),
            'Machines': ', '.join(value.keys()),
        })
        
        for machine, details in value.items():
            if machine is None or pd.isna(machine) or machine == '':
                machine = 'No Machine Assigned'
            
            machine_job_result_list.append({
                'Machine': machine,
                'Main Box': main_box,
                'Count of Jobs': len(details),
            })
            for detail in details:
                job_name, box_name, job_type, owner = detail
                machine_job_log_list.append({
                    'Machine': machine,
                    'Main Box': main_box,
                    'Box Name': box_name,
                    'Job Name': job_name,
                    'Job Type': job_type,
                    'Owner': owner,
                })
                
    for key, value in machine_main_box_dict.items():
        machine = key
        
        machine_analysis_result_list.append({
            'Machine': machine,
            'Count of Main Boxes': len(value),
            'Total Count of Jobs': sum(len(details) for details in value.values()),
            'Main Boxes': ', '.join(value.keys()),
        })
        
        
        
    df_machine_analysis_result = pd.DataFrame(machine_analysis_result_list)
    df_main_box_analysis_result = pd.DataFrame(main_box_analysis_result_list)
    df_machine_job_result = pd.DataFrame(machine_job_result_list)
    df_machine_job_log = pd.DataFrame(machine_job_log_list)

    return df_machine_analysis_result, df_main_box_analysis_result, df_machine_job_result, df_machine_job_log


def createDeploymentSets(df):
    """
    Create deployment sets ensuring all jobs in a mainbox have their machines deployed together
    or already deployed in previous sets.
    """
    deployment_sets = []
    deployed_jobs = set()
    deployed_machines = set()
    
    # Build dictionaries for analysis
    main_box_machine_dict = {}
    machine_main_box_dict = {}
    job_details_dict = {}
    main_box_jobs_dict = {}
    
    for row in df.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        main_box = getattr(row, MAINBOX_COLUMN)
        machine = getattr(row, MACHINE_COLUMN)
        owner = getattr(row, OWNER_COLUMN)

        if job_type == 'BOX':
            continue
        
        # Handle Self Start mainbox
        if main_box == '*Self Start' or main_box == 'Self Start':
            main_box = job_name
            
        if machine is None or pd.isna(machine) or machine == '':
            machine = 'No Machine Assigned'
            
        # Store job details
        job_details_dict[job_name] = {
            'job_name': job_name,
            'job_type': job_type,
            'box_name': box_name,
            'main_box': main_box,
            'machine': machine,
            'owner': owner
        }
        
        # Build mapping dictionaries
        main_box_machine_dict.setdefault(main_box, set()).add(machine)
        machine_main_box_dict.setdefault(machine, set()).add(main_box)
        main_box_jobs_dict.setdefault(main_box, []).append(job_name)
    
    def canDeployMainBox(main_box, additional_machines=set()):
        """Check if all machines required by main_box are available"""
        required_machines = main_box_machine_dict[main_box]
        all_available_machines = deployed_machines.union(additional_machines)
        return required_machines.issubset(all_available_machines)
    
    def getUndeployedMainBoxes():
        """Get main boxes that still have undeployed jobs"""
        undeployed = []
        for main_box in main_box_machine_dict.keys():
            undeployed_jobs = [job_name for job_name in main_box_jobs_dict[main_box] 
                             if job_name not in deployed_jobs]
            if undeployed_jobs:
                undeployed.append(main_box)
        return undeployed
    
    set_number = 1
    
    # Phase 1: Deploy 1 machine with all related mainboxes that use only this machine
    single_machine_candidates = []
    
    for machine, related_mainboxes in machine_main_box_dict.items():
        all_mainboxes_use_only_this_machine = True
        for main_box in related_mainboxes:
            if len(main_box_machine_dict[main_box]) > 1:
                all_mainboxes_use_only_this_machine = False
                break
        
        if all_mainboxes_use_only_this_machine:
            single_machine_candidates.append((machine, related_mainboxes))
    
    # Deploy single machine candidates
    for machine, related_mainboxes in single_machine_candidates:
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box in related_mainboxes:
            jobs_in_mainbox = [job_details_dict[job_name] for job_name in main_box_jobs_dict[main_box] 
                              if job_name not in deployed_jobs]
            
            if jobs_in_mainbox:
                current_set_jobs.extend(jobs_in_mainbox)
                current_set_mainboxes.append(main_box)
        
        if current_set_jobs:
            deploy_type = f'Single Machine ({len(current_set_mainboxes)} MainBoxes)'
            
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': deploy_type,
                'main_boxes': current_set_mainboxes,
                'machines': [machine],
                'new_machines': [machine],
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            deployed_machines.add(machine)
            set_number += 1
    
    # Phase 2: Deploy mainboxes that can be deployed with already deployed machines (zero new machines)
    # เรียงลำดับตามจำนวน machines จากน้อยไปมาก
    while True:
        undeployed_mainboxes = getUndeployedMainBoxes()
        if not undeployed_mainboxes:
            break
            
        # Find mainboxes that can be deployed with current deployed machines (no new machines needed)
        zero_new_machine_candidates = []
        for main_box in undeployed_mainboxes:
            if canDeployMainBox(main_box):  # ใช้ deployed machines เท่านั้น
                machine_count = len(main_box_machine_dict[main_box])
                zero_new_machine_candidates.append((main_box, machine_count))
        
        if not zero_new_machine_candidates:
            break  # ไม่มี mainbox ที่ deploy ได้โดยไม่ต้องเพิ่ม machine ใหม่
        
        # เรียงตามจำนวน machines จากน้อยไปมาก (mainbox ที่ใช้ agent น้อยก่อน)
        zero_new_machine_candidates.sort(key=lambda x: x[1])
        
        print(f"\n=== Phase 2: Zero New Machines ===")
        print(f"Candidates found: {len(zero_new_machine_candidates)}")
        for main_box, machine_count in zero_new_machine_candidates:
            print(f"  - {main_box}: {machine_count} machines")
        
        # Deploy mainboxes เรียงจากที่ใช้ machine น้อยไปมาก
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box, machine_count in zero_new_machine_candidates:
            jobs_in_mainbox = [job_details_dict[job_name] for job_name in main_box_jobs_dict[main_box] 
                              if job_name not in deployed_jobs]
            
            if jobs_in_mainbox:
                current_set_jobs.extend(jobs_in_mainbox)
                current_set_mainboxes.append(main_box)
                print(f"  Added {main_box} with {machine_count} machines ({len(jobs_in_mainbox)} jobs)")
        
        if current_set_jobs:
            # Get all machines used by these mainboxes
            all_machines_in_set = set()
            for main_box in current_set_mainboxes:
                all_machines_in_set.update(main_box_machine_dict[main_box])
            
            # สร้าง deployment type ที่แสดงการเรียงลำดับ
            machine_counts = [len(main_box_machine_dict[mb]) for mb in current_set_mainboxes]
            min_machines = min(machine_counts)
            max_machines = max(machine_counts)
            
            if min_machines == max_machines:
                deploy_type = f'Zero New Machines - {min_machines} Machine MainBoxes ({len(current_set_mainboxes)} boxes)'
            else:
                deploy_type = f'Zero New Machines - {min_machines}-{max_machines} Machine MainBoxes ({len(current_set_mainboxes)} boxes)'
            
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': deploy_type,
                'main_boxes': current_set_mainboxes,
                'machines': list(all_machines_in_set),
                'new_machines': [],  # ไม่มี machine ใหม่
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            # ไม่ต้อง update deployed_machines เพราะไม่มี machine ใหม่
            set_number += 1
            
            print(f"  Created deployment set {set_number - 1} with {len(current_set_mainboxes)} mainboxes")
        else:
            break
    
    # Phase 3: Handle remaining jobs by adding one new machine at a time
    while True:
        undeployed_mainboxes = getUndeployedMainBoxes()
        if not undeployed_mainboxes:
            break
        
        # Find the best mainbox to deploy (requires fewest new machines)
        best_mainbox = min(undeployed_mainboxes, 
                          key=lambda mb: len(main_box_machine_dict[mb] - deployed_machines))
        
        required_machines = main_box_machine_dict[best_mainbox]
        new_machines_needed = required_machines - deployed_machines
        
        if len(new_machines_needed) == 0:
            # This shouldn't happen as Phase 2 should catch this
            continue
        
        # Select one new machine to add
        selected_new_machine = list(new_machines_needed)[0]
        current_machines_in_set = deployed_machines.union({selected_new_machine})
        
        # Find all mainboxes that can be deployed with this machine set
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box in undeployed_mainboxes:
            if canDeployMainBox(main_box, {selected_new_machine}):
                jobs_in_mainbox = [job_details_dict[job_name] for job_name in main_box_jobs_dict[main_box] 
                                  if job_name not in deployed_jobs]
                
                if jobs_in_mainbox:
                    current_set_jobs.extend(jobs_in_mainbox)
                    current_set_mainboxes.append(main_box)
        
        if current_set_jobs:
            # Get all machines used by selected mainboxes
            all_machines_in_set = set()
            for main_box in current_set_mainboxes:
                all_machines_in_set.update(main_box_machine_dict[main_box])
            
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': f'One New Machine ({len(current_set_mainboxes)} MainBoxes)',
                'main_boxes': current_set_mainboxes,
                'machines': list(all_machines_in_set),
                'new_machines': [selected_new_machine],
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            deployed_machines.update(all_machines_in_set)
            set_number += 1
        else:
            break  # Safety break
    
    return deployment_sets


def analyzeDeploymentSets(deployment_sets):
    """Analyze and create summary of deployment sets"""
    summary_list = []
    detail_list = []
    
    for deploy_set in deployment_sets:
        new_machines = deploy_set.get('new_machines', deploy_set['machines'])
        summary_list.append({
            'Set Number': deploy_set['set_number'],
            'Deployment Type': deploy_set['deployment_type'],
            'Main Boxes Count': len(deploy_set['main_boxes']),
            'Total Machines Count': len(deploy_set['machines']),
            'New Machines Count': len(new_machines),
            'Jobs Count': deploy_set['job_count'],
            'Main Boxes': ', '.join(deploy_set['main_boxes']),
            'All Machines': ', '.join(deploy_set['machines']),
            'New Machines': ', '.join(new_machines)
        })
        
        for job in deploy_set['jobs']:
            detail_list.append({
                'Set Number': deploy_set['set_number'],
                'Deployment Type': deploy_set['deployment_type'],
                'Job Name': job['job_name'],
                'Job Type': job['job_type'],
                'Box Name': job['box_name'],
                'Main Box': job['main_box'],
                'Machine': job['machine'],
                'Owner': job['owner']
            })
    
    df_summary = pd.DataFrame(summary_list)
    df_detail = pd.DataFrame(detail_list)
    
    return df_summary, df_detail

def main():
    df_job = getDataExcel("input main ROOT job file")

    df_machine, df_main_box, df_result, df_log = findingmachineAndJob(df_job)
    
    # Create deployment sets
    deployment_sets = createDeploymentSets(df_job)
    df_deploy_summary, df_deploy_detail = analyzeDeploymentSets(deployment_sets)
    
    createExcel(OUTPUT_EXCEL_NAME, 
                (OUTPUT_MACHINE_SHEETNAME, df_machine), 
                (OUTPUT_MAIN_BOX_SHEETNAME, df_main_box), 
                (OUTPUT_RESULT_SHEETNAME, df_result), 
                (OUTPUT_SHEETNAME_LOG, df_log),
                ('Deployment Sets Summary', df_deploy_summary),
                ('Deployment Sets Detail', df_deploy_detail)
                )
    
    
if __name__ == '__main__':
    main()