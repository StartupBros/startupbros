from pathlib import Path

p = Path('clrs/src/solver.jl')
text = p.read_text()

old_sig = '\ttesting=false, # print the times of the first two iterations. This is for testing purposes\n)'
new_sig = '''\ttesting=false, # print the times of the first two iterations. This is for testing purposes
    skip_convert=false,
    converted_sdp_callback=nothing,
)'''
assert text.count(old_sig) == 1, text.count(old_sig)
text = text.replace(old_sig, new_sig, 1)

old_conv = '    sdp = convert_to_prec(sdp, prec) #\n'
new_conv = '''    if !skip_convert
        sdp = convert_to_prec(sdp, prec)
    end
    if !isnothing(converted_sdp_callback)
        converted_sdp_callback(sdp)
    end
'''
assert text.count(old_conv) == 1, text.count(old_conv)
text = text.replace(old_conv, new_conv, 1)

marker = '"""Compute the step length min(γ α(M,dM), 1), where α is the maximum number step\n'
assert text.count(marker) == 1, text.count(marker)
text = text.replace(marker, 'const K5_STEP_VARIANT = Ref(0)\n\n' + marker, 1)

old_eig = '            values, vecs, info = eigsolve(Float64.(tempX[2].blocks[j].blocks[l]), 1, :SR; krylovdim = 10, maxiter = min(100,size(tempX[2].blocks[j].blocks[l],1)),tol=10^-5, issymmetric=true, eager=true, verbosity=0)\n'
new_eig = '''            n_step = size(tempX[2].blocks[j].blocks[l], 1)
            variant = K5_STEP_VARIANT[]
            startvec = [Float64(mod((104729 + 2*variant)*i*i + (12347 + 17*variant)*i + 97 + 7919*variant, 1000003) + 1) for i=1:n_step]
            values, vecs, info = eigsolve(Float64.(tempX[2].blocks[j].blocks[l]), startvec, 1, :SR; krylovdim = 10, maxiter = min(100,n_step),tol=10^-5, issymmetric=true, eager=true, verbosity=0)
'''
assert text.count(old_eig) == 1, text.count(old_eig)
text = text.replace(old_eig, new_eig, 1)

p.write_text(text)
print('PATCH_APPLIED_DETERMINISTIC_STEP')
