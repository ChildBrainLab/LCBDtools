% classdef convertNirsDS
%     methods (Static)
%         function res = convertNirsDS(path)
%             NirsPaths = dir(fullfile(path, '**', '*_fNIRS'));
% 
%             for i = 1:numel(NirsPaths)
%                 fpath = strcat(NirsPaths(i).folder, '/', NirsPaths(i).name);
%                 HomerOfflineConverter(fpath)
%             end
%             
%             res = 1
%         end
%     end
% end
%     

path = "/data/perlman/moochie/study_data/CARE/NIRS_data_preproc/";

NirsPaths = dir(fullfile(path, '**', '*_fNIRS'));

for i = 1:numel(NirsPaths)
    fpath = strcat(NirsPaths(i).folder, '/', NirsPaths(i).name);
    HomerOfflineConverter(fpath)
end