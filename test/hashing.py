import argparse
import adios2                               # pylint: disable=import-error
import numpy as np                          # pylint: disable=import-error
from mpi4py import MPI                      # pylint: disable=import-error

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instream", "-i", help="Name of the input BP5 stream", default="wrfout_d01_2019-11-26_12:00:00")
    parser.add_argument("--outfile", "-o", help="Name of the output BP5 file", default="output.bp")
    return parser.parse_args()

def process_bp5(input_file, output_file):
    comm = MPI.COMM_WORLD  # Get MPI communicator

    # Open input BP5 file
    with adios2.Stream(input_file, "r", comm, "adios2.xml") as fr:
        # Create output BP5 file
        with adios2.Stream(output_file, "w", comm, "hashing.xml") as fw:
            for fr_step in fr:
                cur_step = fr_step.current_step()
                available_vars = fr_step.available_variables()

                # Begin writing step
                fw.begin_step()

                for var_name, var_info in available_vars.items():
                    try:
                        # Read the variable data
                        data = fr_step.read(var_name)

                        # Define variable in output BP5 file
                        var = fw.define_variable(var_name, data.shape, data.shape, (0,), adios2.constant_dims)
                        # ds = fw.io.define_derived_variable("derived/storedata", self.EXPR, DerivedVarType.StoreData)
                        # Write data
                        fw.put(var, data)
                    except Exception as e:
                        print(f"Warning: Could not process variable {var_name}. Error: {e}")

                # End writing step
                fw.end_step()

if __name__ == "__main__":
    args = setup_args()
    process_bp5(args.instream, args.outfile)
