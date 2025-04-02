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
    
    
    
    fr = Stream(io, input_file, "r", mpi.comm_app)
    # Open input BP5 file
   


    
    
    fw = Stream(io2, output_file, "w", MPI.COMM_WORLD)

    for fr_step in fr.steps():
        available_vars = fr_step.AvailableVariables()

        # Begin writing step

        for var_name, var_info in available_vars.items():
            try:
                shape = var_info['Shape'].split(',')
                shape = tuple(map(int, shape)) if shape[0] else ()  # Convert to tuple

                # Read data
                data = fr_step.Read(var_name)
            except Exception as e:
                print(f"Warning: Could not process variable {var_name}. Error: {e}")

        
        fr.EndStep()

    # Close files
    fr.Close()
    fw.Close()

if __name__ == "__main__":
    args = setup_args()
    process_bp5(args.instream, args.outfile)
