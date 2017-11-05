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

def status(args):
    filename = args.filename
    web_api = JemuWebApi()
    result = web_api.check_status(filename)
    print(result.status_code)
    print(result.text)

def download(args):
    filename = args.filename
    local_filename = args.local_filename
    web_api = JemuWebApi()
    web_api.download_jemu(filename, local_filename)


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

    status_parser = subparsers.add_parser('status', help='checks the status of a binary FW file')
    status_parser.add_argument(
        '--filename',
        '-f',
        help='File name of the Binary',
        required=True
    )

    download_parser = subparsers.add_parser('download', help='download files from GCP')
    download_parser.add_argument(
        '--filename',
        '-f',
        help='File name of the Binary',
        required=True
    )
    download_parser.add_argument(
        '--local_filename',
        '-l',
        help='File name of the place to store the file',
        required=True
    )

    args = parser.parse_args()

    if args.command == 'generate':
        generate(args)
    if args.command == 'status':
        status(args)
    if args.command == 'download':
        download(args)


if __name__ == '__main__':
    main()
