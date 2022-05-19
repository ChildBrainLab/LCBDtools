% this script runs the HomerOfflineConverter (which is stored
% next to it) on all of the child folders, of any path depth,
% from the supplied path where the child folder name ends in 
% _fNIRS. It could be modified to handle other use cases as well,
% but this is sufficient for the conversion of the CARE 
% fNIRS dataset. 


path = "/data/perlman/moochie/study_data/P-CAT/NIRS_data_PSU/";

NirsPaths = dir(fullfile(path, '2022*', '*'));
%%
for i = 1:numel(NirsPaths)
    fpath = strcat(NirsPaths(i).folder, '/', NirsPaths(i).name);
    HomerOfflineConverter(fpath)
end