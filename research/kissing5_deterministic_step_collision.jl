include(joinpath(@__DIR__, "..", "clrs", "examples", "ThreePointBound.jl"))
using .ThreePointBound, ClusteredLowRankSolver

const PREC = 192
const COMMON = (
    prec=PREC,
    matmul_prec=PREC,
    preprocess=false,
    duality_gap_threshold=big"1e-80",
    dual_error_threshold=big"1e-80",
    primal_error_threshold=big"1e-80",
    omega_d=10^3,
    omega_p=10^3,
    step_length_threshold=big"1e-30",
    verbose=false,
)

function cmp_matrixvars(a, b)
    @assert Set(keys(a)) == Set(keys(b))
    entries = 0
    nonzero = 0
    maxdiff = BigFloat(0)
    firstdiff = nothing
    for key in sort!(collect(keys(a)), by=string)
        A = Matrix(a[key]); B = Matrix(b[key])
        @assert size(A) == size(B)
        for idx in eachindex(A)
            delta = abs(BigFloat(A[idx]) - BigFloat(B[idx]))
            entries += 1
            if delta != 0
                nonzero += 1
                isnothing(firstdiff) && (firstdiff = (repr(key), idx, string(A[idx]), string(B[idx]), string(delta)))
            end
            maxdiff = max(maxdiff, delta)
        end
    end
    return (entries=entries, nonzero=nonzero, maxdiff=maxdiff, first=firstdiff)
end

function cmp_pair(d1, p1, d2, p2)
    dm = cmp_matrixvars(d1.matrixvars, d2.matrixvars)
    pm = cmp_matrixvars(p1.matrixvars, p2.matrixvars)
    @assert length(d1.x) == length(d2.x)
    xe = 0; xn = 0; xd = BigFloat(0); xf = nothing
    for j in eachindex(d1.x), i in eachindex(d1.x[j])
        delta = abs(BigFloat(d1.x[j][i]) - BigFloat(d2.x[j][i]))
        xe += 1
        if delta != 0
            xn += 1
            isnothing(xf) && (xf = (j, i, string(delta)))
        end
        xd = max(xd, delta)
    end
    @assert Set(keys(p1.freevars)) == Set(keys(p2.freevars)
    fe = 0; fn = 0; fd = BigFloat(0); ff = nothing
    for key in sort!(collect(keys(p1.freevars)), by=string)
        delta = abs(BigFloat(p1.freevars[key]) - BigFloat(p2.freevars[key]))
        fe += 1
        if delta != 0
            fn += 1
            isnothing(ff) && (ff = (repr(key), string(delta)))
        end
        fd = max(fd, delta)
    end
    return (
        entries=dm.entries + pm.entries + xe + fe,
        nonzero=dm.nonzero + pm.nonzero + xn + fn,
        maxdiff=max(dm.maxdiff, pm.maxdiff, xd, fd),
        dual_matrix=dm,
        primal_matrix=pm,
        x_entries=xe,
        x_nonzero=xn,
        x_maxdiff=xd,
        free_entries=fe,
        free_nonzero=fn,
        free_maxdiff=fd,
        first_x=xf,
        first_free=ff,
    )
end

function write_measurement(io, prefix, m)
    for f in (:mu, :d_obj, :p_obj, :dual_gap, :D_error, :d_error, :p_error, :alpha_d, :alpha_p, :beta)
        println(io, prefix, "_", f, '\t', getproperty(m, f))
    end
end

problem, _, _ = three_point_spherical_codes(5, 1//2, 14, 14; COMMON..., maxiterations=0)
sdp_base = ClusteredLowRankSolver.ClusteredLowRankSDP(problem; prec=PREC)
threading = ClusteredLowRankSolver.ThreadingInfo(sdp_base)

converted = Ref{Any}()
direct_states = Dict{Int,Any}()
direct_measurements = Dict{Int,Any}()
ClusteredLowRankSolver.K5_STEP_VARIANT[] = 0

direct_cb = function(m, d, p)
    direct_measurements[m.iter] = m
    if m.iter == 2 || m.iter == 3
        direct_states[m.iter] = (deepcopy(d), deepcopy(p))
    end
end

direct = ClusteredLowRankSolver.solvesdp(
    sdp_base, threading;
    COMMON...,
    maxiterations=3,
    skip_convert=false,
    converted_sdp_callback=s -> (converted[] = s),
    solution_callback=direct_cb,
)

@assert haskey(direct_states, 2) && haskey(direct_states, 3)
@assert haskey(direct_measurements, 3)
d2, p2 = direct_states[2]
d3, p3 = direct_states[3]
sdp = converted[]
return_cmp = cmp_pair(d3, p3, direct.dualsol, direct.primalsol)
@assert return_cmp.entries == 458998 && return_cmp.nonzero == 0

warm0_measure = Ref{Any}()
ClusteredLowRankSolver.K5_STEP_VARIANT[] = 0
warm0 = ClusteredLowRankSolver.solvesdp(
    sdp, threading;
    COMMON...,
    maxiterations=1,
    skip_convert=true,
    dualsol=d2,
    primalsol=p2,
    iteration_callback=m -> (warm0_measure[] = m),
)
cmp0 = cmp_pair(d3, p3, warm0.dualsol, warm0.primalsol)

warm1_measure = Ref{Any}()
ClusteredLowRankSolver.K5_STEP_VARIANT[] = 1
warm1 = ClusteredLowRankSolver.solvesdp(
    sdp, threading;
    COMMON...,
    maxiterations=1,
    skip_convert=true,
    dualsol=d2,
    primalsol=p2,
    iteration_callback=m -> (warm1_measure[] = m),
)
cmp1 = cmp_pair(d3, p3, warm1.dualsol, warm1.primalsol)

@assert cmp0.entries == cmp1.entries == 458998
@assert cmp1.nonzero > 0

# Independent exact comparator control.
d3_bad = deepcopy(d3)
p3_bad = deepcopy(p3)
bad_key = first(sort!(collect(keys(d3_bad.matrixvars)), by=string))
bad_delta = setprecision(BigFloat, PREC) do
    BigFloat(2)^(-100)
end
d3_bad.matrixvars[bad_key][1,1] += bad_delta
bad_cmp = cmp_pair(d3, p3, d3_bad, p3_bad)
@assert bad_cmp.entries == 458998
@assert bad_cmp.nonzero == 1
@assert bad_cmp.maxdiff == bad_delta

open("results/summary.tsv", "w") do io
    println(io, "status\tPASS")
    println(io, "solver_commit\t09ac81aed031bdea714832cf515244f6eb223531")
    println(io, "krylovkit_version\t0.10.4")
    println(io, "precision\t", PREC)
    println(io, "threads\t", Threads.nthreads())
    println(io, "direct_q3_entries\t", return_cmp.entries)
    println(io, "direct_return_nonzero\t", return_cmp.nonzero)
    println(io, "deterministic_same_entries\t", cmp0.entries)
    println(io, "deterministic_same_nonzero\t", cmp0.nonzero)
    println(io, "deterministic_same_maxdiff\t", cmp0.maxdiff)
    println(io, "deterministic_same_first_dual\t", repr(cmp0.dual_matrix.first))
    println(io, "deterministic_same_first_primal\t", repr(cmp0.primal_matrix.first))
    println(io, "alternate_start_entries\t", cmp1.entries)
    println(io, "alternate_start_nonzero\t", cmp1.nonzero)
    println(io, "alternate_start_maxdiff\t", cmp1.maxdiff)
    println(io, "alternate_start_first_dual\t", repr(cmp1.dual_matrix.first))
    println(io, "alternate_start_first_primal\t", repr(cmp1.primal_matrix.first))
    println(io, "bad_key\t", repr(bad_key))
    println(io, "bad_delta\t", bad_delta)
    println(io, "bad_nonzero\t", bad_cmp.nonzero)
    println(io, "direct_primal_objective\t", direct.primalobj)
    println(io, "direct_dual_objective\t", direct.dualobj)
    println(io, "warm0_primal_objective\t", warm0.primalobj)
    println(io, "warm0_dual_objective\t", warm0.dualobj)
    println(io, "warm1_primal_objective\t", warm1.primalobj)
    println(io, "warm1_dual_objective\t", warm1.dualobj)
    write_measurement(io, "direct3", direct_measurements[3])
    write_measurement(io, "warm0", warm0_measure[])
    write_measurement(io, "warm1", warm1_measure[])
end

open("results/result.json", "w") do io
    print(io, "{\n")
    print(io, "  \"deterministic_same_nonzero\": ", cmp0.nonzero, ",\n")
    print(io, "  \"alternate_start_nonzero\": ", cmp1.nonzero, ",\n")
    print(io, "  \"comparator_control_nonzero\": ", bad_cmp.nonzero, "\n")
    print(io, "}\n")
end

println("DETERMINISTIC_STEP_COLLISION_COMPLETE")
