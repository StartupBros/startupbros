from pathlib import Path

p = Path('clrs/src/solver.jl')
text = p.read_text()

old_sig = '\ttesting=false, # print the times of the first two iterations. This is for testing purposes\n)'
new_sig = '\ttesting=false, # print the times of the first two iterations. This is for testing purposes\n    skip_convert=false,\n    converted_sdp_callback=nothing,\n    internal_state_callback=nothing,\n    mirror_warmstart_upper=false,\n)'
assert text.count(old_sig) == 1, text.count(old_sig)
text = text.replace(old_sig, new_sig, 1)

old_conv = '    sdp = convert_to_prec(sdp, prec) #\n'
new_conv = '    if !skip_convert\n        sdp = convert_to_prec(sdp, prec)\n    end\n    if !isnothing(converted_sdp_callback)\n        converted_sdp_callback(sdp)\n    end\n'
assert text.count(old_conv) == 1, text.count(old_conv)
text = text.replace(old_conv, new_conv, 1)

old_import = '                    if !isnothing(dualsol)\n                        X.blocks[j].blocks[k][hs, vs] = dualsol.matrixvars[bl]\n                    end\n                    if !isnothing(primalsol)\n                        Y.blocks[j].blocks[k][hs, vs] = primalsol.matrixvars[bl]\n                    end\n'
new_import = '                    if !isnothing(dualsol)\n                        X.blocks[j].blocks[k][hs, vs] = dualsol.matrixvars[bl]\n                        if mirror_warmstart_upper && r != s\n                            X.blocks[j].blocks[k][vs, hs] = transpose(Matrix(dualsol.matrixvars[bl]))\n                        end\n                    end\n                    if !isnothing(primalsol)\n                        Y.blocks[j].blocks[k][hs, vs] = primalsol.matrixvars[bl]\n                        if mirror_warmstart_upper && r != s\n                            Y.blocks[j].blocks[k][vs, hs] = transpose(Matrix(primalsol.matrixvars[bl]))\n                        end\n                    end\n'
assert text.count(old_import) == 1, text.count(old_import)
text = text.replace(old_import, new_import, 1)

initial_marker = '    #check sizes:\n'
initial_callback = '    if !isnothing(internal_state_callback)\n        internal_state_callback(:initial, 0, x, X, y, Y, sdp)\n    end\n'
assert text.count(initial_marker) == 1, text.count(initial_marker)
text = text.replace(initial_marker, initial_callback + initial_marker, 1)

post_marker = '        # saving the solution\n'
post_callback = '        if !isnothing(internal_state_callback)\n            internal_state_callback(:post_update, iter, x, X, y, Y, sdp)\n        end\n'
assert text.count(post_marker) == 1, text.count(post_marker)
text = text.replace(post_marker, post_callback + post_marker, 1)

p.write_text(text)
print('PATCH_APPLIED_INTERNAL_STATE_COLLISION')
