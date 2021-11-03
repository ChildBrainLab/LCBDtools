#!/bin/csh

set program = $0; set program = $program:t
echo $program $argv[1-]
if (${#argv} < 1) then
	echo "usage:	"$program" patid [day1_patid]"
	echo " "
	exit 1
endif

if (${#argv} > 1) then
	set patid = $1
	set day1_patid = $2
	@ day1 = 1
endif

if (${#argv} == 1) then
	set patid = $1
	set day1_patid = $patid
	@ day1 = 0
endif



if (-e $cwd/$patid/SCANS.studies.txt) then
	set dicom = $cwd/$patid/SCANS.studies.txt
else if (-e $cwd/scans.studies.txt) then
	set dicom = $cwd/scans.studies.txt
endif
set num_lines = `cat $dicom | wc -l`
	
set bold = ("")
set irun = ("")	
set t2 = ("")
set mpr = ("")
set sefm_AP = ("")
set sefm_PA = ("")
#set sefm = ("")

# MM fix a string problem in the new task names (lacking "AP" after the task name)
#sed -ri 's/Task([0-9]+)/Task\1_PA/' $dicom

sed -ri 's/TASK/Task/' $dicom

# MM fixing another problem (case of no sequence number after the rest/task designation)
#sed -ri 's/_MB[0-9][a-zA-Z0-9_.]*(_SBRef)?/\1/' $dicom
#sed -ri 's/_MB[468]_2.[04](.*fr)?//' $dicom
#sed -ri 's/(REST|Task|TASK)_/\11_/' $dicom

# MM fix extra junk at the end of fieldmap names
sed -ri 's/(Map_(AP|PA))_[a-zA-Z0-9_.]+/\1/' $dicom

@ i = 1
while ( $i <= $num_lines )
	set line = `cat $dicom | head -$i | tail -n1`
	set description = `echo $line | awk '{print $2}'` 
	set study_num = `echo $line | awk '{print $1}'`
	switch ($description)
		case tfl3d1_16ns:
			set mpr = ($mpr $study_num)
			breaksw;
		case spc_314ns:
			set t2 = ($t2 $study_num)
			breaksw;
		case epse2d1_90:
			set sefm_name = `echo $line | awk '{print $3}'`
			if ($sefm_name == 'SpinEchoFieldMap_AP') then
				set sefm_AP = ($sefm_AP $study_num)
			else if ($sefm_name == 'SpinEchoFieldMap_PA') then
				set sefm_PA = ($sefm_PA $study_num)
			endif
			breaksw;
		case epfid2d1_90:
			set bold_name = `echo $line | awk '{print $3}'`
			set ref = `echo $line | awk '{print $3}' | rev | cut -d '_' -f1 | rev`
			set str = `echo $bold_name | awk '{print substr($0, 7, 4)}' | tr "[a-z]" "[A-Z]"`
			set num = `echo $bold_name | perl -ne '/(\d+)/; print ($1 || 1);'` # extract task number from bold_name; if none found, assume 1
#		   set num = `echo $num | sed -r 's/^([0-9])$/0\1/'` # if task number is just a single digit, pad it with a leading zero (for sorting convenience)
			if ($ref == SBRef) then
				echo skipping the SBRef
			else
				set bold = ($bold $study_num)
				switch ($str)
					case TASK:
					set run = Task${num}
					breaksw;
					case REST:
					set run = $num
					breaksw;
					case AUDI:
					set run = AuditoryTask${num}
					breaksw;
				endsw
				set irun = ($irun $run)
			endif
		breaksw;
	endsw
	@ i++
end

@ i = 1
set rest = ("")
while ($i <= ${#irun})
	set rest_name = `echo $irun | awk '$'$i' !~ /Task/ {print $'$i'}'`
	set rest = ($rest $rest_name)
	@ i++
end


set paramsfile = ${patid}.params
set fcparamsfile = fc.params

if (-e  $paramsfile) then
	rm $paramsfile
endif
touch $paramsfile

if (-e  $fcparamsfile) then
	rm $fcparamsfile
endif
touch $fcparamsfile

@ n_mpr = ${#mpr}
@ n_t2 = ${#t2}

echo "set patid	= " ${patid} >> $paramsfile
echo "set mprs	= (" $mpr[$n_mpr] ")" >> $paramsfile
echo "set tse	= (" $t2[$n_t2] ")" >> $paramsfile
echo "set fstd	= (" $bold ")">> $paramsfile
echo "set irun = (" $irun ")" >> $paramsfile
#echo "set irun = ( Task1 Task2 Task3 Task4 Task5 Task6 Task7 )" >> $paramsfile
if ($day1 != 0) then
	echo "set day1_patid = " $day1_patid >> $paramsfile
	echo "set day1_path = " $day1_path >> $paramsfile
endif

if (-e  $fcparamsfile) then
	/bin/rm $fcparamsfile;
	touch $fcparamsfile
endif
	
echo "set boldruns = (" $rest ")" >> $fcparamsfile

	
