# perf-script-postprocessor

This calculates delta (difference of timestamps from various
entry/exit points from events recorded) from the trace output,
which is produced by using the `perf script` command, which in turn,
uses the perf.data file produced by using the `perf record` command,
a set of utilities,which is provided under the package [perf-tools](https://github.com/brendangregg/perf-tools)

## INSTALLATION

`$ sudo ./install`

## USAGE

```
$ perf_script_processor <dir path>
```

`<dir path>` is where one of the following exists:

- perf.data -- binary file. If you're running this tool on perf.data, make sure
		you're running it from the system where the binary was generated
- raw_perf -- plain text output when `perf script` is run on folder containing perf.data
- perf_data.csv -- generated in the process of generating results

#### EXPLANATION 

`perf_scirpt_processor` calls a python script `delta_processor` with options set to default as follows:

```delta_processor -i ${DUMP_PATH%/}/perf_data.csv -o $DUMP_PATH -m 3```

However if you wanna use the `delta_processor` script directly, to utilize more options, use it like this:

```
DUMP_PATH='/tmp/pp_results/'

delta_processor --input=$DUMP_PATH'/perf_data.csv' --output=$DUMP_PATH --conf=<conf path> --mode=<0,1,2,3>

```

* Either set an env var DUMP_PATH as you would like it to be 
  and use that throughout the session, or supply a custom path.. 
  Just ensure that script has write permssions to the folder.

* Generate delta of events for data from `perf script`[3]. 
  

* This script runs in 3 modes. Those being:

    - `Mode 0`: Produce `delta_processed.csv` with __all events together__[2].
    - `Mode 1`: In addition to mode 0, this calculates __loop statistics__[1].
    - `Mode 2`: breakup result into __per-event calculated delta csv files__.
    - `Mode 3`: only calculates __loop statistics__ (from perf_data.csv).

* [1] Set this in `/etc/delta_processor.conf`. Default is as below:

```
[Pattern] 

# native
order = kvm_exit syscallssys_exit_ppoll syscallssys_enter_io_submit syscallssys_exit_io_submit

# thread
# order = kvm_exit syscallssys_exit_ppoll syscallssys_enter_pread64 syscallssys_exit_pread64
```

* [2] Events are like this:
	
	```
		kvm___
		sched_switch
		syscallssys__futex
		syscallssys__io_getevents
		syscallssys__io_submit
		syscallssys__ppoll
		syscallssys__pwrite64
		syscallssys__pwritev
	```
	
	For detailed list, refer this [perf.txt](https://gist.githubusercontent.com/staticfloat/ad064cd6ae653f2afba7/raw/324a81a7423dd94226bd7ad3d1035a517612720f/perf.txt)	

* [3] Check more options for script through `$ delta_processor -h`

Note: 
perf_data.csv is produced by using the perf_script_processor command.
This is incase, one has already produced the csv file from a previous run
of postprocessor script.

## FAQ

* Why are graphs not generated for the results?

	The flame graphs can be generated for such a dataset. Refer to [this blog](http://www.brendangregg.com/perf.html#FlameGraphs). But if one needs to see
	the y axis points, well they're really present in a huge amount, ofcourse,
	which could be handled through analytical methods later on. But for now,
	this doesn't support such analysis. (given the number of loops in resultant data). 
	Hence we leave it to only producing a delta in a csv file.

* How much time does it take for the tool to generate results?

	Depends on the size of your extracted data (plain text) from perf.data. 
	For a 1.5 Gb raw_perf, the script takes about 40-45 secs on an Intel model 
	`name	: Intel(R) Xeon(R) CPU X5365  @ 3.00GHz`. 

* How do I know the script isn't stuck and is actually running?

	The script at the beginning of the test, in a few sec, would produce an stdout like this
	```
	Unique metrics found:
	  syscallssys__ppoll
	  syscallssys__pread64
	  kvm___
	```
	
	This means the data has been loaded, and keys have been processed. It then calls
	the `prepare_delta()` method which processed loop deltas. The result of that would 
	add on to the stdout like this:
	
	```
	 **********************
	 delta:exit_ppoll__kvm_exit stats:
	  Standard Dev: xxx
	  Mean: xxx
	  Median: xxx
	 ======================
	 delta:enter_pread64__exit_ppoll stats:
	  Standard Dev: xxx
	  Mean: xxx
	  Median: xxx
	 ======================
	 delta:exit_pread64__enter_pread64 stats:
	  Standard Dev: xxx
	  Mean: xxx
	  Median: xxx
	 ======================
	 Script was executed with Mode option 3.
	 Results have been stored to: thread/
	 Time taken -- prepare_delta() -- 41.4485499859
	```
	In addition, it will produce a	`loop_diff.csv` and a `perf_data.csv` in the output dir.
	
	If it doesn't, Well :shit: . 

## LICENSE

GPL V3


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/arcolife/perf-script-postprocessor/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

