import argparse

class Extension():
    # Class-level attributes for parsed arguments with default values
    mode = "none"

    @classmethod
    def parse_arguments(cls, args):

        # Initialize the argument parser
        parser = argparse.ArgumentParser(description="Nadzoru 2 Extension Configuration")
        
        # Add arguments
        parser.add_argument(
            "--mode", 
            type=cls.validate_mode,  # Custom validation function
            choices=["none", "prob", "public", "probpub"],  # Only allow these values
            default="none", 
            help="Set the extension to use (choices are 'none', 'prob', 'public', 'probpub')")

        # Parse arguments and update class attributes
        args = parser.parse_args(args)
        
        # Store parsed arguments as class attributes
        cls.mode = args.mode

        print(f"Extension Mode: {cls.mode}")

    @classmethod
    def validate_mode(cls, mode):
        # Normalize input for mode
        if mode in ["prob", "probability", "probabilistic"]:
            return "prob"       # Normalize to "prob"
        elif mode in ["pub", "public"]:
            return "public"     # Normalize to "public"
        elif mode in ["probpub", "probabilitypublic", "probabilisticpublic"]:
            return "probpub"    # Normalize to "probpub"
        return mode