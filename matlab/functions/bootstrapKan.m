function [R, H, RHx] = bootstrapKan(rec, dt, pslow, vp, nmax)
% Bootstap error calculation for grid search confidence.
% [Vp, R, H, VpRmax, Hmax] = bootstrap(rec, Tps, dt, pslow, nmax)
% Outputs are arrays of best estimates of Vp, R and H along with the
% the maximum values in the solution space (stacked amplitudes) for the
% Vp & R grid search and the H line search. These can be used for error
% contours to go along with estimates of parameters uncertainty.


rec = rec';
n = size(rec,2);
R = zeros(1, nmax);
H = zeros(1, nmax);
RHx = zeros(1, nmax);
parfor ii = 1:nmax
    ind = randi(n, n, 1);
    [R(ii), H(ii), RHx(ii) ] = gridsearchKanC( rec(:, ind), dt, pslow(ind), vp);
end


%Vp = zeros(workers, iters);
%R = zeros(workers, iters);
%H = zeros(workers, iters);
%VpRmax = zeros(workers, iters);
%Hmax = zeros(workers, iters);
%parfor ii = 1:workers
%   [Vp(ii,:), R(ii,:), H(ii,:), VpRmax(ii,:), Hmax(ii,:)] = bootstrapC(rec, Tps, dt, pslow, iters,ii*100);
%end
%Vp = Vp(:);
%R = R(:);
%H = H(:);
%VpRmax = VpRmax(:);
%Hmax = Hmax(:);





