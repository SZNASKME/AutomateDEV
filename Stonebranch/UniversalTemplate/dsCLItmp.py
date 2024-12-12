import time
import subprocess
import argparse
import sys
import logging,os
version = "1.0.0"
purpose = "Datastage Integration"
logging.basicConfig(level="${ops_ds_log_level}", format=' %(asctime)s - %(levelname)s - %(message)s')
####Get input parameters
def script_setup():
    parser=argparse.ArgumentParser(description='Purpose : Trigger IBM datastage job via dsjob CLI')
    
    # ## --> Capture Universal Task Form Variables Here
    parser.add_argument('--job_name', default="${ops_ds_job}")
    parser.add_argument('--param', default="${ops_ds_param}")
    parser.add_argument('--wait', default="${ops_ds_wait}")
    parser.add_argument('--reset', default="${ops_ds_reset_mode}")
    parser.add_argument('--project', default="${ops_ds_project}")
    parser.add_argument("--ds_user_name", default="${_credentialUser('${ops_ds_cred}')}")
    parser.add_argument('--ds_user_password', default="${_credentialPwd('${ops_ds_cred}')}")
                                                  
    parser.add_argument('--print_logs', default='${ops_ds_print_logs}')
    parser.add_argument('--server', default='${ops_ds_server}')
    parser.add_argument('--domain', default='${ops_ds_domain}')
    # ## --
    global args
    args = parser.parse_args()
    # ## --> Logging info
    parser.add_argument("--logginglevel", default="info")
    logging.info("Executing version " + version + " with the following paramaters")
    logging.info(args)
# --
###########################################################################################
# Datastage universal Template to run the Job
###########################################################################################
def run_job():
    logging.info(" Setting the DSJob Command")
    try:
        logging.info("Check the parameters")
        other_options_str = ""
        other_options = []
        if args.param:
            other_options.append(args.param)
        if args.wait == "true":
            other_options.append("-jobstatus")
            logging.info("Job will be monitored till the execution is completed")
        if args.reset == "true":
            other_options.append("-mode RESET")
            logging.info("Reset the Job option enabled")

        other_options_str = " ".join(other_options)

        dsjob_command="dsjob -server "+args.server+" -domain " + args.domain + " -user " + args.ds_user_name \
            +" -password " + args.ds_user_password + " -run " + other_options_str + " "+args.project+" "+args.job_name
        
        logging.info("DSJOB Command : "+str(dsjob_command))
        exec_response = os.system(dsjob_command)
        logging.info("Job Run Output:"+str(exec_response))
        if exec_response == 0:
            logging.info("DataStage Job executed Successfully")
            print("job ran successfully")
            sys.exit(0)
        else:
            logging.error("Problems in Job execution")
            sys.exit(int(exec_response))
    except Exception as e:
        logging.error("Error with DSJOB run:"+str(e))
        sys.exit(1) 
#
###########################################################
# Main Function 
###########################################################
def main():
    script_setup()
    run_job()
    if args.print_logs=="true":
        logging.info("Attempting to print the job log")
        log_command="dsjob -logdetail "+args.project+" "+args.job_name
        logging.info("Log fetch command:"+str(log_command))
        log_output=subprocess.check_output(log_command,shell=True)
        log_output_decode=log_output.decode("utf-8")
        print("Job Execution Logs :")
        print(log_output_decode) 

# -- Main Logic Function
if __name__ == '__main__':
    main()