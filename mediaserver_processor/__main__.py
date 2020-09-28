import argparse
import asyncio

from mediaserver_processor.image_processor import MediaServerProcessor


def main():
    """
    Main entry point for the application

    Returns
    -------
    None
    """
    parser = create_parser()
    args = parser.parse_args()
    app = MediaServerProcessor()

    if args.config:
        app.load_config(args.config)

    if args.disable_logging:
        app.config['DISABLE_LOGGING'] = True

    app.broadcast_welcome_message()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print('\nStopped watching... Goodbye.')


def create_parser():
    """
    Creates the argument parser that is necessary to parse optional arguments with CLI.

    Returns
    -------
    parser : argparse.ArgumentParser
        The parser that handles all argument parsing.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='config file to load from', type=str, metavar='')
    parser.add_argument('--disable-logging', help='if set, disables all logs', action='store_true')
    return parser


if __name__ == '__main__':
    main()
