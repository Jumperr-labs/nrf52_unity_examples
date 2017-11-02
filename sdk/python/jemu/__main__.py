from __future__ import print_function

from os import path
import argparse

from .jemu_web_api import JemuWebApi


def generate(args):
    file_path = args.bin.name
    filename = path.basename(file_path)
    emulator = path.join(path.dirname(file_path), '{}.jemu'.format(filename))
    web_api = JemuWebApi()
    web_api.create_emulator(filename, args.bin.read(), emulator)


def main():
    parser = argparse.ArgumentParser(
        prog='jumper-cli',
        description="CLI interface for using Jumper's emulator"
    )
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    generate_parser = subparsers.add_parser('generate', help='Generates an emulator from a binary FW file')
    generate_parser.add_argument(
        '--bin',
        '-b',
        type=file,
        help='Binary file used to generate the FW from',
        required=True
    )

    args = parser.parse_args()
    print(args.bin.name)
    if args.command == 'generate':
        generate(args)


if __name__ == '__main__':
    main()
