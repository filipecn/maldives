#!/usr/bin/py
import os
from b3_register import B3Register
import argparse
    
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("directory", type=str, help="b3 historical data directory path")
    parse.add_argument("negotiationCode", type=str, help="negotiation code (ex: VALE5)")
    args = parse.parse_args()    
    with open(args.negotiationCode + '_registers.txt', 'w') as out:
        for filename in os.listdir(args.directory):
            file = args.directory + '/' + filename
            with open(file, 'r') as f:
                print('reading from ' + file)
                lines = f.readlines()
                for i in range(1, len(lines)-1):
                    b3Register = B3Register(lines[i])
                    if b3Register.attributes['negotiationCode'] == args.negotiationCode:
                        out.write(lines[i])
