import argparse
import sys
from ..api import Invaria

def main():
    parser = argparse.ArgumentParser(description="Invaria — Universal LLM Context Compiler")
    subparsers = parser.add_subparsers(dest="command")

    compress_parser = subparsers.add_parser("compress", help="Compress a context")
    compress_parser.add_argument("input_file", help="Input file path")
    compress_parser.add_argument("--mode", default="invariant", help="Compression mode")

    verify_parser = subparsers.add_parser("verify", help="Verify a compressed context")
    verify_parser.add_argument("original", help="Original context file")
    verify_parser.add_argument("compressed", help="Compressed context file")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    compiler = Invaria()

    if args.command == "compress":
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        result = compiler.compress(text, mode=args.mode)
        
        print(f"Original tokens (approx): {result.original_tokens}")
        print(f"Compressed tokens (approx): {result.compressed_tokens}")
        print(f"Reduction: {result.token_reduction}")
        print(f"Ratio: {result.compression_ratio:.2f}")
        print(f"Verified: {result.proof.verified}")
        print("\n--- COMPRESSED OUTPUT ---")
        print(result.text)

    elif args.command == "verify":
        with open(args.original, 'r', encoding='utf-8') as f:
            orig_text = f.read()
        with open(args.compressed, 'r', encoding='utf-8') as f:
            comp_text = f.read()
            
        is_valid = compiler.verify(orig_text, comp_text)
        print(f"Verification Passed: {is_valid}")

if __name__ == "__main__":
    main()
