from __future__ import (print_function)
from time import sleep
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import event
from universal_extension import logger
from universal_extension import ui
from universal_extension.deco import dynamic_choice_command
import subprocess,os,sys


class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

        # Flag to control the event loop below
        self.run = True
    
    ###################################################
    #dynamic command to fetch the project list
    ####################################################
    @dynamic_choice_command("project")
    def primary_choice_command(self, fields):
        logger.info("Intiating CLI Call to Datastage")
        try:
            # Run the dsjob command to list jobs for the specified project
            if fields['specific_server']:
                command = ['dsjob', '-lprojects', '-server', fields['server'], '-user', fields['cred.user'], '-password', fields['cred.password']]
            else:
                command = ['dsjob', '-lprojects', '-user', fields['cred.user'], '-password', fields['cred.password']]
            logger.info("Command:"+str(command))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            # Check for errors
            if process.returncode != 0:
                print(f"Error executing dsjob command: {error}")
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'project_name'",
                    values = ["Error occured"]
                    )
            else:
                # Parse the output to extract job names
                projects = [line.strip() for line in output.split('\n') if line.strip()]
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'project_name'",
                    values = projects
                    )
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "Error Occured"
    ###################################################
    #dynamic command to fetch the Jobs list
    ####################################################
    @dynamic_choice_command("job")
    def primary_choice_command(self, fields):
        logger.info("Intiating CLI Call to Datastage to fetch Jobs list")
        try:
            # Run the dsjob command to list jobs for the specified project
            if fields['specific_server']:
                command = ['dsjob', '-ljobs', '-server', fields['server'], '-user', fields['cred.user'], '-password', fields['cred.password'],fields['project'][0]]
            else:
                command = ['dsjob', '-ljobs', '-user', fields['cred.user'], '-password', fields['cred.password'],fields['project'][0]]
            logger.info("Command:"+str(command))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            # Check for errors
            if process.returncode != 0:
                print(f"Error executing dsjob command: {error}")
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'Job List'",
                    values = ["Error occured"]
                    )
            else:
                # Parse the output to extract job names
                jobs = [line.strip() for line in output.split('\n') if line.strip()]
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'jobs'",
                    values = jobs
                    )
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "Error Occured"
    ###################################################
    #dynamic command to fetch the Jobs parameters List
    ####################################################
    @dynamic_choice_command("available_param")
    def primary_choice_command(self, fields):
        logger.info("Intiating CLI Call to Datastage to fetch Job's Parameters")
        try:
            # Run the dsjob command to list jobs for the specified project
            if fields['specific_server']:
                command = ['dsjob', '-lparams '+fields['job'][0], '-server', fields['server'], '-user', fields['cred.user'], '-password', fields['cred.password'],fields['project'][0]]
            else:
                command = ['dsjob', '-lparams '+fields['job'][0], '-user', fields['cred.user'], '-password', fields['cred.password'],fields['project'][0]]
            logger.info("Command:"+str(command))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            # Check for errors
            if process.returncode != 0:
                print(f"Error executing dsjob command: {error}")
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'Job List'",
                    values = ["Error occured"]
                    )
            else:
                # Parse the output to extract job names
                jobs = [line.strip() for line in output.split('\n') if line.strip()]
                return ExtensionResult(
                    rc = 0,
                    message = "Values for choice field: 'jobs'",
                    values = jobs
                    )
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return "Error Occured"


    def extension_start(self, fields):
        logger.info("Execute DSjob CLI to trigger Datastage Job")
        #call datastage function
        self.load_profile(fields)
        self.run_job(fields)
    
    #############################################################################
    # Function to trigger Datastage 
    ###############################################################################
    
    def load_profile(self,fields):
        logger.info("Loading the Datastage Profile")
        try:
            profile_command=". "+fields['profile_file']
            profile_response = subprocess.run(profile_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if profile_response.returncode == 0:
                logger.info("Datastage Profile Loaded Successfully")
            else:
                logger.error("Error in Loading Datastage Profile")
                logger.error("Error Message: "+str(profile_response.stderr))
                os._exit(1)
        except Exception as e:
            logger.error("Error with profile loading:"+str(e))
            os._exit(1)

    
    def run_job(self,fields):
        logger.info("In Run Job Function :")
        try:
            logger.info("Check the parameters")
            other_options_str = ""
            other_options = []
            ### Arrange Params 
            if len(fields['param']) ==0 :
                logger.info("No Parameters Considered for execution")
            else:
                for item in fields['param']:
                    for key, value in item.items():
                        other_options_str += f"-param {key}={value} "
                other_options_str = other_options_str.strip()
                logger.info("Parameters :"+str(other_options_str))
            #####Parameter Processing Completed
            if fields['wait']:
                other_options.append("-jobstatus")
                logger.info("Job will be monitored till the execution is completed")
            if fields['reset_mode']:
                other_options.append("-mode RESET")
                logger.info("Reset the Job option enabled")
            other_options_str = " ".join(other_options)
            profile_command = ". "+fields["profile_file"]+" && "
            if fields["specific_server"]:
                job_command = "dsjob -server "+fields['server']+" -domain " +fields['domain']+ " -user " + fields['cred.user'] \
            +" -password " + fields['cred.password'] + " -run " + other_options_str + " "+fields['project'][0]+" "+fields['job'][0]
            else:
                job_command = "dsjob -user " + fields['cred.user'] +" -password " + fields['cred.password'] \
            + " -run " + other_options_str + " "+fields['project'][0]+" "+fields['job'][0]
            dsjob_command = profile_command + job_command
            logger.debug("dsjob_command:"+str(dsjob_command))
            exec_response = subprocess.run(dsjob_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug("Job Run Output:"+str(exec_response))
            if exec_response.returncode == 0:
                logger.info("DataStage Job executed Successfully")
                print("job ran successfully")
                if fields['print_logs']:
                    self.fetch_logs(fields)
                os._exit(0)
            else:
                logger.error("Problems in Job execution")
                logger.error("Error Message:"+str(exec_response.stderr))
                self.fetch_logs(fields)
                os._exit(exec_response.returncode)
        except Exception as e:
            logger.error("Error with DSJOB run:"+str(e))
            os._exit(1)
#
    #############################################################################
    # Function to fetch logs
    ###############################################################################
    def fetch_logs(self,fields):
        logger.info("Attempting to fetch logs:")
        profile_command=". "+fields['profile_file'] + " && "
        log_command = profile_command + "dsjob -logdetail "+fields['project'][0]+" "+fields['job'][0]
        logger.info("Log fetch command:"+str(log_command))
        try:
            log_output=subprocess.check_output(log_command,shell=True)
            log_output_decode=log_output.decode("utf-8")
            print("Job Execution Logs :")
            print(log_output_decode)
        except Exception as e:
            logger.error("Failure to fetch the Logs :"+str(e))



