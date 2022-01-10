% this script runs the HomerOfflineConverter (which is stored
% next to it) on all of the child folders, of any path depth,
% from the supplied path where the child folder name ends in 
% _fNIRS. It could be modified to handle other use cases as well,
% but this is sufficient for the conversion of the CARE 
% fNIRS dataset. 


path = "/data/perlman/moochie/study_data/CARE/NIRS_data_preproc/";

NirsPaths = dir(fullfile(path, '**', '*_fNIRS'));
%%
for i = 1:numel(NirsPaths)
    fpath = strcat(NirsPaths(i).folder, '/', NirsPaths(i).name);
    HomerOfflineConverter(fpath)
end