import sys


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args:
        from server.server import main as run_cli

        return run_cli(args)

    from server.gui import UDPRelayGUI

    app = UDPRelayGUI()
    app.run()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
