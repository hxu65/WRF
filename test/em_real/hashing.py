import argparse
import adios2
import numpy as np
from mpi4py import MPI

def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instream", "-i", help="Name of the input BP5 stream", default="wrfout_d01_2019-11-26_12:00:00")
    parser.add_argument("--outfile", "-o", help="Name of the output BP5 file", default="output.bp")
    return parser.parse_args()

def process_bp5(input_file, output_file):
    comm = MPI.COMM_WORLD  # Get MPI communicator
    adios = adios2.ADIOS(comm)  # Initialize ADIOS
    
    # Open input BP5 file
    io_in = adios.DeclareIO("InputIO")
    fr = io_in.Open(input_file, adios2.Mode.Read, comm)

    # Create output BP5 file
    io_out = adios.DeclareIO("OutputIO")
    fw = io_out.Open(output_file, adios2.Mode.Write, comm)

    while fr.BeginStep() == adios2.StepStatus.OK:
        cur_step = fr.CurrentStep()
        available_vars = io_in.AvailableVariables()

        # Begin writing step
        fw.BeginStep()

        for var_name, var_info in available_vars.items():
            try:
                # Read metadata to get shape
                shape = var_info['Shape'].split(',')
                shape = tuple(map(int, shape)) if shape[0] else ()  # Convert to tuple

                # Read data
                data = fr.Read(var_name)

                # Define variable in output BP5 file
                if var_name not in io_out.AvailableVariables():
                    io_out.DefineVariable(var_name, data, shape, shape, (0,), adios2.ConstantDims)

                # Write data
                fw.Put(var_name, data)
            except Exception as e:
                print(f"Warning: Could not process variable {var_name}. Error: {e}")

        # End writing step
        fw.EndStep()
        fr.EndStep()

    # Close files
    fr.Close()
    fw.Close()

if __name__ == "__main__":
    args = setup_args()
    process_bp5(args.instream, args.outfile)
