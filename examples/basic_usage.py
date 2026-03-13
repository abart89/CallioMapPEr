# Basic usage example — placeholder.
#
# Demonstrates the minimal workflow:
#   1. Point the Translator at a Calliope model directory.
#   2. Optionally provide an epistemic sidecar.
#   3. Optionally provide a results.nc path.
#   4. Call translate() and save the output .nq file.
#
# Example (to be implemented once M1 is complete):
#
#   from calliomapper import Translator
#
#   t = Translator(
#       model_dir="path/to/calliope_model/",
#       sidecar="path/to/epistemic_sidecar.yaml",
#       results="path/to/results.nc",
#   )
#   graph = t.translate()
#   t.save("output/my_model.nq")
