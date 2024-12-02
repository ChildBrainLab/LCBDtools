import LCBDtools.Stimuli as stimuli
from stimuli import Flanker
from stimuli import ATV
from stimuli import Motor
from stimuli import DB_DOS

class annotator:
	def __init__(self):
		return
	
    def load_covariates(self, study, subject, nirs):
		# if covariates file is available, load its series for the subject
        if covariates != None:
			idx = covariates[covariates['subject'] == str(subject)].index
			if len(idx) == 0:
				print("Subject not found in covariates file.")
				print("Skipping:", ses)
		        continue
		    elif len(idx) > 1:
				print("Subject is duplicated in covariates file.")
				print("Skipping:", ses)
	            continue
		    else:
		        metaSeries = []
	            metaCols = []

	            for col in [col for col in df.columns if "subject" != col]:
	                metaSeries.append(df.iloc[idx[0]][col])
	                metaCols.append(col)
					
    def tasks(self, study, subject, nirs):
	    # if task data is available, load it as an object
		if task_dir is not None:
	        task_fnames = glob(join(task_dir+"/{}/*{}*/*{}*.csv".format(
	            subject, task, task.lower())))

	        if len(task_fnames) == 0:
	            print("No task data found for this participant.")
	            print("Failure to find task data, skipping:", ses)
	            continue

	        elif len(task_fnames) > 1:
	            print("Too many task data found for this participant.")
	            print("Failure to find task data, skipping:", ses)
	            continue

	        task_fname = task_fnames[0]

	        # switch for run type? to pick which loader?
			task = task.lower()
	        if 'flanker' in task:
				self.flanker()
			if 'db-dos' in task:
				self.DB_DOS()
			if 'atv' in task:
				self.ATV()
			if 'motor' in task:
				self.MotorTask()


 	def flanker(self):
        try:
            # load Flanker Object from psychopy file
            flanker_series = Flanker.TaskReader(task_fname).flankerSeries
            task_sub = os.path.basename(task_fname)[:participant_num_len]
            if subject != task_sub:
                print("Warning. Task file may be named incorrectly.")
                print("See:", task_fname, "with session", ses)

            for flank in flanker_series:
                # evaluate flanker data and assign meta data?
                flank.eval()
                # add covariate data into flank object (because)
                if covariates is not None:
                    for j, col in enumerate(metaCols):
                        flank.meta[col] = metaSeries[j]
        except:
            print("Problem encountered when loading Flanker data.")
            print("Failure, skipping:", ses)
            continue

        durations = {
            'Directional': 63,
            'Indirectional': 31.5}

        # this is the joining of the Flanker psychopy information
        # into the MNE raw object
        try:
            events, event_dict = mne.events_from_annotations(
                raw,
                verbose=False)

            if len(events) == 20:
                pass

            elif len(events) == 21:
                raw.annotations.delete(0)

            elif len(events) == 11:
                print("Weird session with 11 flanks. Unsure how to proceed.")
                print("Skipping:", ses)
                continue

            else:
                print("Unfamiliar number of events. Skipping:", ses)
                continue

            # clean up so we only have starts (fixation)
            # by deleting every 2nd index from annotations
            raw.annotations.delete([
                range(1, len(raw.annotations), 2)])

            # rename and set durations for each
            # 315 seconds total for directional,
            # 157.5 total for non-directional
            # can't rename individually?
            length = len(raw.annotations)

            # try just separating based off alternating indexes
            dir_annot = raw.annotations.copy()[range(0, len(raw.annotations), 2)]
            indir_annot = raw.annotations.copy()[range(1, len(raw.annotations), 2)]

            dir_annot.rename({'1.0': 'Directional'})
            indir_annot.rename({'1.0': 'Indirectional'})

            # recombine and fix into raw obj
            raw.set_annotations(
                dir_annot.__add__(indir_annot))

            raw.annotations.set_durations(durations, verbose=True)

            events, event_dict = mne.events_from_annotations(
                raw,
                verbose=False)

            subject = raw.info['subject_info']['his_id'][:participant_num_len]

        except:
            print("Something when wrong when processing the task " +\
                "info into the MNE raw object.")
            print("Skipping:", ses)
            continue

	def ARV(self):
		return

	def DB_DOS(self):
		return

	def MotorTask(self):
		return
