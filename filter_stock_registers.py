#!/usr/bin/py

from b3_register import B3Register
import argparse
    
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("file", type=str, help="b3 historical data .txt file")
    parse.add_argument("negotiationCode", type=str, help="negotiation code (ex: VALE5)")
    args = parse.parse_args()    
    with open(args.negotiationCode + '_registers.txt', 'w') as out:
        with open(args.file, 'r') as f:
            lines = f.readlines()
            out.write(lines[0])
            for i in range(1, len(lines)-1):
                b3Register = B3Register(lines[i])
                if b3Register.attributes['negotiationCode'] == args.negotiationCode:
                    out.write(lines[i])
            out.write(lines[-1])
