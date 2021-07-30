#!/bin/env python
"""
Create configuration file to make data/emulation comparisons for one run.
"""
import os, argparse, shutil

def check_setup():
    """Check that valid proxy is available; needed to
    access DAS."""
    exit_code = os.system('voms-proxy-info -exists')
    if(exit_code != 0):
        print "Obtain valid proxy with 'voms-proxy-init -voms cms -rfc'"
        return False
    else:
        return True

def main():
    """Generate configuration file given primary dataset,
    conditions, run period, and era."""
    primary_dataset = 'HcalNZS'
    conditions = '112X_dataRun3_HLT_v3'
    period = 'Commissioning2021'
    era = 'Run3'

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--run", required = True)
    parser.add_argument('-g', "--globaltag")
    parser.add_argument('-p', "--runperiod")
    parser.add_argument('-e', "--era")
    parser.add_argument('-t', "--type")
    args = parser.parse_args()
    runnumber = args.run
    if(args.globaltag):
        conditions = args.globaltag
    if(args.runperiod):
        period = args.runperiod
    if(args.type):
        primary_dataset = args.type
        
    if(primary_dataset != "local" and check_setup()):
        filename = 'filelist_' + runnumber + '_' + primary_dataset + '.txt'
        output_filename = "\\\'analyze_" + runnumber + ".root\\\'"

        # get filelist from DAS
        das_command = 'dasgoclient --query="file dataset=/' \
            + primary_dataset + '/' + period + '-v1/RAW run=' \
            + runnumber + '" > ' + filename
        print "Getting filelist using DAS query:\n" + das_command
        os.system(das_command)

        # generate cmsDriver.py command
        cmsdriver_command = "cmsDriver.py" \
            + " analyze --data --conditions " + conditions \
            + " -s RAW2DIGI --geometry DB:Extended --era " + era \
            + " --customise Debug/HcalDebug/customize.compare_raw_reemul_tp" \
            + " --customise Debug/HcalDebug/customize.use_data_reemul_tp" \
            + " --customise_commands" \
            + " process.TFileService.fileName=cms.string\(" + output_filename + "\)" \
            + " --filein=filelist:" + filename \
            + " --python_filename=analyze_" + runnumber + ".py" \
            + " --no_exec -n -1 --no_output " 
        print "Using cmsDriver.py command:\n" + cmsdriver_command
        os.system(cmsdriver_command)

    # HcalTBSource cannot currently be specified in a cmsDriver.py command
    # so a special treatment is necessary
    else:
        newfile = 'analyze_2021_tp_data_' + runnumber + '.py'
        shutil.copy2('analyze_2021_tp_data_LOCALBASE.py', newfile)
        os.system("sed -i 's/RUNNUMBER/" + runnumber + "/' " + newfile)
        os.system("sed -i 's/GLOBALTAG/" + conditions + "/' " + newfile)
                     
main()
