%
% Align and Stack P-wave coda for source estimation
%
clear all
close all

loadtools;
addpath([userdir,'/programming/matlab/jsonlab'])
addpath ../../sac
addpath ../functions
rootdir = '/media/TerraS/CN/';

json = loadjson([userdir,'/thesis/data/eventSources.json']);

fields = fieldnames(json);

events = cell(1, length(fields));

split = @(s) (s(7:end));

for ii = 1:length(fields)
    events{ii} = split(fields{ii});
end


num = 50;
stns = cellstr(json.(fields{num}));


%% Extract SAC data
for ii = 1 : length(stns)
    files{ii} = fullfile(rootdir, stns{ii}, events{num}, 'stack_P.sac');  %#ok<*SAGROW>
end

[trace, header] = getTrace(files);

%% Strip out stations with unique delta
dtDiff = 0;
dt = header{1}.DELTA;
for ii = 1: length(header)
    if dt ~= header{ii}.DELTA
        fprintf('Error, station %s has a unique dt\n', header{ii}.KSTNM)
        dtDiff(ii) = 1;
    end
end
if dtDiff
    dtDiff = dtDiff == 1;
    trace(dtDiff, :) = [];
    header(dtDiff) = [];
end
%% Normalize
trace = (diag(1./max( abs(trace), [], 2)) ) * trace;

%% Collect array of Pick times
for ii = 1 : length(header)
    picktimes(ii) = header{ii}.T1 - header{ii}.B;
    endtimes(ii) = header{ii}.T3 - header{ii}.B; 
end

%% Loop through different windows
endwin = 60: -1 : -20;

for ii = 1:length(endwin)
%% Set a window
w1 = round((min(picktimes) + 0) / dt);
w2 = round((max(endtimes) - endwin(ii) ) / dt);

%% normalize traces
wtrace = (diag(1./max( abs(trace(:, w1 : w2)), [], 2)) ) * trace(:, w1 : w2 );

%% Get lags
[tdel, rmean, sigr] = mccc(wtrace, dt);
%% Shift unwindowed traces
strace = lagshift(trace, tdel, dt);

%% PLOT
%figure(2)

Y(ii) = norm(var(strace, 0, 1));

numt = size(strace,1);
figure(3)
subplot(3,1,1)
    plot(trace(1,:))
    line([w1, w2; w1, w2] , [-1, -1; 1, 1])
subplot(3,1,2)
    plot(strace(:, 400:2000)', '--')
    title(sprintf('w2 set at %i, norm of variances = %1.4f', endwin(ii), Y(ii)))
subplot(3,1,3)
    plot(sum(strace(:, 400:2000)) / numt )
pause(0.1)
end

figure()
plot(endwin, Y)