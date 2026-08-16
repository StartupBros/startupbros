include(joinpath(@__DIR__, "..", "clrs", "examples", "ThreePointBound.jl"))
using .ThreePointBound, ClusteredLowRankSolver, Arblib

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

struct SnapshotStop <: Exception end

mutable struct CatStat
    entries::Int
    nonzero::Int
    mid_nonzero::Int
    rad_nonzero::Int
end

function exact_parts(z)
    return Base.decompose(Arblib.midref(z)), Base.decompose(Arblib.radref(z))
end

function row_blocks(sdp, j, l)
    sizes = [size(first(values(sdp.A[j][l][1,r])), 1) for r=1:size(sdp.A[j][l],1)]
    return reduce(vcat, [fill(r, sizes[r]) for r in eachindex(sizes)])
end

function compare_internal(refstate, candstate, sdp)
    xr, Xr, yr, Yr = refstate
    xc, Xc, yc, Yc = candstate
    cats = Dict{String,CatStat}()
    totals = Ref((entries=0, nonzero=0, mid_nonzero=0, rad_nonzero=0))
    firstdiff = Ref{Any}(nothing)

    function account(comp, cat, label, a, b)
        amid, arad = exact_parts(a)
        bmid, brad = exact_parts(b)
        md = amid != bmid
        rd = arad != brad
        df = md || rd
        key = string(comp, ":", cat)
        st = get!(cats, key) do
            CatStat(0,0,0,0)
        end
        st.entries += 1
        st.nonzero += df
        st.mid_nonzero += md
        st.rad_nonzero += rd
        t = totals[]
        totals[] = (
            entries=t.entries + 1,
            nonzero=t.nonzero + df,
            mid_nonzero=t.mid_nonzero + md,
            rad_nonzero=t.rad_nonzero + rd,
        )
        if df && isnothing(firstdiff[])
            firstdiff[] = (
                component=comp,
                category=cat,
                label=label,
                reference_mid=amid,
                candidate_mid=bmid,
                reference_rad=arad,
                candidate_rad=brad,
            )
        end
        return nothing
    end

    @assert size(xr) == size(xc)
    for i in eachindex(xr)
        account("x", "represented", string(i), xr[i], xc[i])
    end

    @assert length(Xr.blocks) == length(Xc.blocks)
    for j in eachindex(Xr.blocks), l in eachindex(Xr.blocks[j].blocks)
        A = Xr.blocks[j].blocks[l]
        B = Xc.blocks[j].blocks[l]
        @assert size(A) == size(B)
        rb = row_blocks(sdp, j, l)
        @assert length(rb) == size(A,1) && size(A,1) == size(A,2)
        for col=1:size(A,2), row=1:size(A,1)
            cat = rb[row] >= rb[col] ? "represented" : "omitted_upper"
            account("X", cat, string(j, ",", l, ",", row, ",", col), A[row,col], B[row,col])
        end
    end

    @assert size(yr) == size(yc)
    for i in eachindex(yr)
        account("y", "represented", string(i), yr[i], yc[i])
    end

    @assert length(Yr.blocks) == length(Yc.blocks)
    for j in eachindex(Yr.blocks), l in eachindex(Yr.blocks[j].blocks)
        A = Yr.blocks[j].blocks[l]
        B = Yc.blocks[j].blocks[l]
        @assert size(A) == size(B)
        rb = row_blocks(sdp, j, l)
        @assert length(rb) == size(A,1) && size(A,1) == size(A,2)
        for col=1:size(A,2), row=1:size(A,1)
            cat = rb[row] >= rb[col] ? "represented" : "omitted_upper"
            account("Y", cat, string(j, ",", l, ",", row, ",", col), A[row,col], B[row,col])
        end
    end

    t = totals[]
    return (
        entries=t.entries,
        nonzero=t.nonzero,
        mid_nonzero=t.mid_nonzero,
        rad_nonzero=t.rad_nonzero,
        cats=cats,
        firstdiff=firstdiff[],
    )
end

function write_comparison(io, prefix, cmp)
    println(io, prefix, "_entries\t", cmp.entries)
    println(io, prefix, "_nonzero\t", cmp.nonzero)
    println(io, prefix, "_mid_nonzero\t", cmp.mid_nonzero)
    println(io, prefix, "_rad_nonzero\t", cmp.rad_nonzero)
    println(io, prefix, "_firstdiff\t", repr(cmp.firstdiff))
    for key in sort!(collect(keys(cmp.cats)))
        safe = replace(key, ":"=>"_")
        st = cmp.cats[key]
        println(io, prefix, "_", safe, "_entries\t", st.entries)
        println(io, prefix, "_", safe, "_nonzero\t", st.nonzero)
        println(io, prefix, "_", safe, "_mid_nonzero\t", st.mid_nonzero)
        println(io, prefix, "_", safe, "_rad_nonzero\t", st.rad_nonzero)
    end
end

function import_and_compare(sdp, threading, d2, p2, refstate; mirror=false)
    result = Ref{Any}()
    callback = function(phase, iter, x, X, y, Y, local_sdp)
        if phase == :initial
            result[] = compare_internal(refstate, (x,X,y,Y), local_sdp)
            throw(SnapshotStop())
        end
    end
    try
        ClusteredLowRankSolver.solvesdp(
            sdp, threading;
            COMMON...,
            maxiterations=0,
            skip_convert=true,
            dualsol=d2,
            primalsol=p2,
            mirror_warmstart_upper=mirror,
            internal_state_callback=callback,
        )
        error("snapshot callback did not stop")
    catch e
        e isa SnapshotStop || rethrow()
    end
    return result[]
end

problem, _, _ = three_point_spherical_codes(5,1//2,14,14; COMMON..., maxiterations=0)
sdp_base = ClusteredLowRankSolver.ClusteredLowRankSDP(problem; prec=PREC)
threading = ClusteredLowRankSolver.ThreadingInfo(sdp_base)

converted_ref = Ref{Any}()
internal_q2 = Ref{Any}()
public_q2 = Ref{Any}()

internal_callback = function(phase, iter, x, X, y, Y, sdp)
    if phase == :post_update && iter == 2
        internal_q2[] = (deepcopy(x), deepcopy(X), deepcopy(y), deepcopy(Y))
    end
end
solution_callback = function(measurements, dualsol, primalsol)
    if measurements.iter == 2
        public_q2[] = (deepcopy(dualsol), deepcopy(primalsol))
    end
end

direct_result = ClusteredLowRankSolver.solvesdp(
    sdp_base, threading;
    COMMON...,
    maxiterations=2,
    skip_convert=false,
    converted_sdp_callback=s->(converted_ref[]=s),
    internal_state_callback=internal_callback,
    solution_callback=solution_callback,
)

@assert isassigned(internal_q2)
@assert isassigned(public_q2)
@assert isassigned(converted_ref)
refstate = internal_q2[]
d2, p2 = public_q2[]
sdp = converted_ref[]

unmirrored = import_and_compare(sdp, threading, d2, p2, refstate; mirror=false)
mirrored = import_and_compare(sdp, threading, d2, p2, refstate; mirror=true)

# Independent adversary: perturb one represented public coordinate by exactly 2^-100.
d2_bad = deepcopy(d2)
p2_bad = deepcopy(p2)
bad_key = first(sort!(collect(keys(d2_bad.matrixvars)), by=string))
bad_delta = setprecision(BigFloat, PREC) do
    BigFloat(2)^(-100)
end
d2_bad.matrixvars[bad_key][1,1] += bad_delta
adversarial = import_and_compare(sdp, threading, d2_bad, p2_bad, refstate; mirror=true)

@assert unmirrored.entries == mirrored.entries == adversarial.entries == 458998
@assert adversarial.nonzero == mirrored.nonzero + 1
@assert adversarial.mid_nonzero == mirrored.mid_nonzero + 1
@assert adversarial.rad_nonzero == mirrored.rad_nonzero
@assert adversarial.cats["X:represented"].nonzero == mirrored.cats["X:represented"].nonzero + 1

open("results/summary.tsv", "w") do io
    println(io, "status\tPASS")
    println(io, "solver_commit\t09ac81aed031bdea714832cf515244f6eb223531")
    println(io, "precision\t", PREC)
    println(io, "threads\t", Threads.nthreads())
    write_comparison(io, "unmirrored", unmirrored)
    write_comparison(io, "mirrored", mirrored)
    write_comparison(io, "adversarial", adversarial)
    println(io, "bad_key\t", repr(bad_key))
    println(io, "bad_delta\t", bad_delta)
    println(io, "direct_primal_objective\t", direct_result.primalobj)
    println(io, "direct_dual_objective\t", direct_result.dualobj)
end

open("results/result.json", "w") do io
    print(io, "{\n")
    print(io, "  \"unmirrored_nonzero\": ", unmirrored.nonzero, ",\n")
    print(io, "  \"mirrored_nonzero\": ", mirrored.nonzero, ",\n")
    print(io, "  \"adversarial_nonzero\": ", adversarial.nonzero, "\n")
    print(io, "}\n")
end

println("INTERNAL_STATE_COLLISION_V3_COMPLETE")
