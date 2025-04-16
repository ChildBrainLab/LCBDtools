% Define runtime variables
numOfSub = 1;
numSessions = 1;
numOfSess = numSessions;
numComp = 78;
viewingSet = 1:numComp;
diffTimePoints = 1;
num_Regress = 10;
num_DataSets = numSessions;
outputDir = '/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/ICA_Test/temporal_sorting/'; % Output directory
sortingCriteria = 'multiple regression';
sortingType = 'temporal';
icasig = [];

% Create variables for storing info
input_resampled_ref = cell(numOfSub, 1);
input_icaTimecourse = cell(numOfSub, 1);
input_modelTimecourse = cell(numOfSub, 1);

% Add info into sesInfo variable
sesInfo.userInput.numOfSub = numOfSub; % Number of subjects
sesInfo.userInput.numOfSess = numSessions; % Number of sessions per subject
sesInfo.numOfSess = numSessions;
sesInfo.userInput.numComp = numComp; % Number of ICA components
sesInfo.userInput.inputFiles = cell(numOfSub, 1);
subjects = num2cell(1:numOfSub);
selectedSubjects = arrayfun(@(x) sprintf("%d"), subjects, 'UniformOutput', false); % Selected subjects
sesInfo.outputDir = outputDir;
sesInfo.userInput.temporal_sorting_method = 'multiple regression'; 
sesInfo.userInput.temporal_sorting_comp = 1:78; 

% Create reference info structure for temporal sorting
refInfo = struct();
refInfo.num_Regress = num_Regress;  % Store number of regressors
refInfo.num_DataSets = num_DataSets;  % Store number of datasets
refInfo.selectedRegressors = struct('name', {});  % Empty structure array
refInfo.spmMatFlag = true;

% Create variables reflecting input_data_subjects.m
modalityType = 'fMRI';
TR = 0.81
group_ica_type = 'spatial';
parallel_info.mode = 'serial';
parallel_info.num_workers = 4;
keyword_designMatrix = 'diff_sub_diff_sess';

dataSelectionMethod = 3;
input_directory_name = '/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE_GIFT/';
subject_dir_regexp = 'sub-\w+';
session_dir_regexp = '';
data_file_pattern = '4D.nii';
file_numbers_to_include = [];
spm_stats_dir = '/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/';

prefix = "emotional_valence"
maskFile = ["/storage1/fs1/perlmansusan/Active/moochie/"];

% Grab all nifti file paths to subject data
input_nifti_files = dir("/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE_GIFT/**/4D.nii");

% Define subject-specific SPM.mat file paths
input_spm_files = dir("/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/sub-*/first_level_analysis/SPM.mat");

% Store subject-specific SPM.mat file paths
sesInfo.userInput.spmMatFiles = fullfile({input_spm_files.folder}, {input_spm_files.name}); 
input_spm_filenames = sesInfo.userInput.spmMatFiles;

% Load each subject's SPM.mat design matrix and extract the condition regressors
for subj = 1:numOfSub
    sesInfo.userInput.inputFiles{subj} = fullfile(input_nifti_files(subj).folder, input_nifti_files(subj).name);
    
    spm = load(sesInfo.userInput.spmMatFiles{subj}, 'SPM');
    design_matrix = spm.SPM.xX.X; % Extract design matrix (conditions over time);
    
    % Assume the first column of X represents the main task condition
    ref_func = design_matrix(:,1:num_Regress);  

    % Grab timecourse file
    tc_file = sprintf('/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/ICA_Analysis/CARE_sub%03d_timecourses_ica_s1_.nii', subj);
    if exist(tc_file, 'file')
       data = load_nii(tc_file);
       input_icaTimecourse{subj} = data.img;
    else
        error("Missing timecourse file for %d", subj);
    end

    num_timepoints_ica = size(input_icaTimecourse{subj}, 1);
    num_timepoints_ref = size(ref_func, 1);

    input_resampled_ref{subj} = resample(ref_func, num_timepoints_ica, num_timepoints_ref);

    % Save resampled reference function
    sub_resampled = input_resampled_ref{subj}
    save(sprintf('/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/ICA_Test/input_resampled_reference_%d.mat', subj), 'sub_resampled');

    sesInfo.userInput.referenceFunction{subj} = sprintf('/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE2024/ICA_Test/input_resampled_reference_%d.mat', subj);

    % Add regressor info
    for i = 1:num_Regress
        refInfo.selectedRegressors(subj, i).name = sprintf('Regressor_%d_Subj_%d', i, subj);
    end

    refInfo.input_modelTimecourse = input_modelTimecourse; % Store reference regressors

    disp(['Subject ', num2str(subj), ' NIfTI: ', input_nifti_files(subj).folder]);
    disp(['Subject ', num2str(subj), ' SPM: ', input_spm_files(subj).folder]);

    input_prefix = sprintf('CARE_sub%d', subj);

    refData = load(sesInfo.userInput.referenceFunction{subj}); 
    input_modelTimecourse{subj} = double(refData.sub_resampled);
     
    refInfo.SPMFile = input_spm_filenames{subj};
    refInfo.modelIndex = subj;
    
    % Call icatb_sortComponents for each subject
    sorted_Components{subj} = icatb_sortComponents('sortingCriteria', sortingCriteria, ...
        'sortingType', sortingType, ...
        'icaTimecourse', input_icaTimecourse{subj}, ...
        'modelTimecourse', input_modelTimecourse{subj}, ...
        'icasig', icasig, ...
        'input_spm_filenames', input_spm_filenames{subj}, ...
        'numSubjects', 1, ...
        'numSessions', 1, ...
        'numOfSess', 1, ...
        'numSess', 1, ...
        'numComp', numComp, ...
        'diffTimepoints', diffTimePoints, ...
        'num_Regress', num_Regress, ...
        'num_DataSets', num_DataSets, ...
        'refInfo', refInfo, ...
        'viewingSet', viewingSet, ...
        'output_dir', outputDir, ...
        'input_prefix', sprintf('CARE_sub%d', subj), ...
        'num_sort_subjects', 1, ...
        'num_sort_sessions', 1);
end
