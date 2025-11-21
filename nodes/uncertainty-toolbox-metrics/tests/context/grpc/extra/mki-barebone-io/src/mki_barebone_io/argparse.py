import argparse


def argparse_execution_message() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--func", type=str, help="<Required> Function name")
    parser.add_argument("--input_uri", nargs="+", help="<Required> URI to input resources", required=True)
    parser.add_argument("--output_uri", nargs="+", help="<Required> URI to output resources", required=True)

    args = parser.parse_args()

    exec_message = dict(
        func=args.func,
        input=[dict(location=dict(uri=uri)) for uri in args.input_uri],
        output=[dict(location=dict(uri=uri)) for uri in args.output_uri],
        meta=dict()
    )

    return exec_message
