import argparse

class Extension():
    # Class-level attributes for parsed arguments with default values
    mode = "none"

    class ModeAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # Only set the mode if it hasn't been set yet
            if getattr(namespace, 'mode', None) is None:
                setattr(namespace, 'mode', self.const)

    @classmethod
    def parse_arguments(cls, args):
        # Initialize the argument parser
        parser = argparse.ArgumentParser(description="Nadzoru 2 Extension Configuration")
        
        # Add mutually exclusive group for mode flags
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--none", dest='mode', action=cls.ModeAction, const='none', nargs=0, help="Set mode to 'none'. Use no extensions.")
        group.add_argument("--prob", dest='mode', action=cls.ModeAction, const='prob', nargs=0, help="Set mode to 'prob'. Use probabilistic events extension.")
        group.add_argument("--public", dest='mode', action=cls.ModeAction, const='public', nargs=0, help="Set mode to 'public'. Use public events extension.")
        group.add_argument("--probpub", dest='mode', action=cls.ModeAction, const='probpub', nargs=0, help="Set mode to 'probpub'. Use probabilistic and public events extension.")

        # Parse arguments and update class attributes
        args = parser.parse_args(args)
        
        # Store parsed arguments as class attributes
        cls.mode = args.mode if args.mode else "none"

        print(f"Extension Mode: {cls.mode}")