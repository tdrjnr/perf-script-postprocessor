#!/usr/bin/env python3
# coding: utf-8

# Author: Archit Sharma <archit.py@gmail.com>
# Makes use of data generated by using `perf script`
# ref: http://linux.die.net/man/1/perf-script

# Explaining why graphs are not generated for the delta:
# df_dict contains keys as metrics and values and "entry and exit" 
# points for those metrics. even if we create diff'ed version between 
# entry and exit, the no of x-axis points would be be large enough,
# given the length of all kvm entries and size of entry/exit points. 
# Even if this is plotted in nvd3, I don't think one would be able to 
# make out the differences that minute.. Hence we leave it to only producing
# a delta in a huge csv file.


import os, sys
import argparse
import pandas as pd

class PostProcessor(object):
    '''
    Form a DataFrame from the csv and utilize 
    inhouse functions to calculate delta. '''
    def __init__(self, csv_fpath, res_path='/tmp/pp_results'):
        self.file_path = csv_fpath
        self.df_dict = {}
        # self._figsize = (13.5,8)
        self.result_path = res_path
        
    def load_data(self):
        self.df = pd.read_csv(self.file_path)
        self.df.convert_objects(convert_numeric=True)
        self.df['tstamp'] = self.df.apply(lambda row: row.tstamp*1000000, axis=1)
        # print(self.df.dtypes)
        # print(len(self.df))
        
    def _process(self, x):
        ''' 
        clean the metric keys to get unique categories.
        Example: kvm_entry/kvm_exit represents kvm as a category
        '''
        return x.replace('_exit_','__').replace('_exit','___')\
                .replace('_entry','___').replace('_enter_','__')
    
    def _process_inverse(self, entry, alternate=False):
        '''
        convert those categories back to metric name as under
        perf script processed data. '''
        if not alternate:
            return entry.replace('___','_exit').replace('___','_entry')\
                        .replace('__','_exit_').replace('__','_enter_')
        else:
            # observe the order of enter/exit is different
            return entry.replace('___','_entry').replace('___','_exit')\
                        .replace('__','_enter_').replace('__','_exit_')    

    def _unique_metrics(self):
        """
        `___` would mean this is meant to be replaced by `_entry`
        and `_exit` later -> special case for kvm_entry/exit
        
        `__` would mean this is meant to be replaced by `_enter_`
        and `_exit_` later -> preserves kvm_entry/exit
        
        `_` would mean no changes -> preserves sched_switch
        """
        self.entries = self.df['entry'].unique().tolist()
        if pd.np.nan in self.entries:
            self.entries.remove(pd.np.nan)
        self.entries = set([self._process(i) for i in self.entries])
        print("Unique metrics found:\n\t%s"%'\n\t'.join(self.entries))

    def prepare_delta(self, break_up=False):
        # load data
        self.load_data()
        # prepare list of metric categories
        self._unique_metrics()
        # prepare dict of dataframes with keys as category
        for entry in self.entries:
            self.df_dict[entry] = self.df[(self.df['entry'] == self._process_inverse(entry)) |\
                                (self.df['entry'] == self._process_inverse(entry, alternate=True))]

        # if per-metric csv's are required, generate them!
        if break_up:
            try:
                os.mkdir(self.result_path)
            except FileExistsError as E:
                print("Dir exists..")
            except PermissionError as E:
                quit("Permission Error. Results Dir cannot be created!")
            except:
                raise
            
            for key in self.df_dict.keys():
                self.df_dict[key].set_index('entry').diff().to_csv('%s.csv'%(os.path.join(self.result_path, key)))
            print("Per-metric results have been stored to %s"%(self.result_path))
        else:
            # TODO: if breakup isn't specified, join the 
            # dataframes into one single frame and dump that
            pass

            
if __name__=='__main__':
   # Parse configurations
    parser = argparse.ArgumentParser(description="""Generate delta of entry/exit points 
    for data from `perf script`. Example:
    
    ./delta_processor.py --input=dumps/perf_data.csv --output=dumps/ --per_metric=True""")
    parser.add_argument('--input', type=str, help='Absolute Path to input csv file')
    parser.add_argument('--output', type=str, help='Absolute Path to output dir')    
    parser.add_argument('--per_metric', type=bool, help='breakup the result file into per-metric csv delta files')
    args = parser.parse_args()
    try:
        if not args.input:
            if sys.argv[1]:
                PP = PostProcessor(sys.argv, res_path=args.output)
            else:
                PP = PostProcessor('perf_data.csv', res_path='.')
            Delta = PP.prepare_delta()
        else:
            if args.output:
                PP = PostProcessor(args.input, res_path=args.output)
            else:
                PP = PostProcessor(args.input)
            if args.per_metric:
                Delta = PP.prepare_delta(break_up=True)
            else:
                Delta = PP.prepare_delta()
    except Exception as E:
        quit("%s\nUnable to execute. Refer to --help. I Quit!"%(E))