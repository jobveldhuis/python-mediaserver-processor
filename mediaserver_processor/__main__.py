import argparse
import asyncio

from mediaserver_processor.app import MediaServerProcessor


def main():
    parser = create_parser()
    args = parser.parse_args()
    app = MediaServerProcessor()

    if args.config:
        app.load_config(args.config)

    if args.command == 'run':
        app.broadcast_welcome_message()
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(app.run())
        except KeyboardInterrupt:
            print('\nStopped watching... Goodbye.')

    elif args.command == 'single':
        # TODO: Write logic for parsing a single image
        pass


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='command to run', choices=['run', 'single'])
    parser.add_argument('-c', '--config', help='config file to load from', type=str, metavar='')
    return parser


if __name__ == '__main__':
    main()
