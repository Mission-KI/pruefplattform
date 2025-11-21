from urllib.parse import urlparse, urlunparse
import os
import fsspec
from typing import List

try:
    import pyarrow as pa
    from schema import Schema, And, Optional, Use
except ImportError:
    raise ImportError("Please install pyarrow and schema to use Apache Arrow io features")

DATATYPES = {  # not a complete list, yet
    "null": pa.null,
    "bool": pa.bool_,
    "bool8": pa.bool8,
    "int8": pa.int8,
    "int16": pa.int16,
    "int32": pa.int32,
    "int64": pa.int64,
    "uint8": pa.uint8,
    "uint16": pa.uint16,
    "uint32": pa.uint32,
    "uint64": pa.uint64,
    "float16": pa.float16,
    "float32": pa.float32,
    "float64": pa.float64,
    "time32": pa.time32,
    "time64": pa.time64,
    "timestamp": pa.timestamp,
    "date32": pa.date32,
    "date64": pa.date64,
    "string": pa.string,
    "binary": pa.binary,
    "uuid": pa.uuid,
}

table_schema = Schema(
    And(
        [  # List of fields...
            {
                "name": And(str, len),
                "type": And(str, lambda x: x in DATATYPES.keys(), error="Invalid data type"),
                Optional("nullable"): Use(bool),
                Optional("metadata"): Schema({str: str}),
            }
        ],
        len,  # ... that shouldn't be empty
    )
)


def parse_schema(schema_def: List[dict]) -> pa.Schema:
    schema_def = [
        pa.field(
            name=f["name"],
            type=DATATYPES[f["type"]](),
            nullable=f.get("nullable", False),
            metadata=f.get("metadata", None),
        )
        for f in table_schema.validate(schema_def)
    ]
    return pa.schema(schema_def)


def load_arrow(artifact_node_msg: dict, schema: pa.Schema, **fs_args) -> List[pa.Table]:
    """Load a batch of tables from an Apache Arrow file (IPC)
    Args:
        artifact_node_msg (dict): An artifact node message
        schema (pa.Schema): the schema of the arrow table
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer

    Raises:
        NotImplementedError: If trying to load a resource / file format that is not supported

    Returns:
        List[pa.Table]: The batch of Apache Arrow tables
    """

    uri = artifact_node_msg["location"]["uri"]
    parsed_uri = urlparse(uri)

    file_path = parsed_uri.path
    _, ext = os.path.splitext(file_path)

    if ext == ".arrow":
        fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

        batches = []
        with fs.open(uri, "rb") as source:
            reader = pa.RecordBatchFileReader(source)
            for batch_index in range(reader.num_record_batches):
                batch = reader.get_record_batch(batch_index)
                batches.append(batch)
        return batches

    raise NotImplementedError(f"Expected a file with the 'arrow' file extension (got '{ext}').")


def hash_arrow():
    pass


def store_arrow(
    tables: List[pa.Table], artifact_node_message: dict, schema: pa.Schema, hash_obj: bool = True, **fs_args
) -> dict:
    """Store a batch of Apache Arrow tables to uri

    Args:
        tables (List[pa.Table]): The batch of Apache Arrow tables
        artifact_node_message (dict): Output artifact node message
        schema (pa.Schema): the schema of the arrow tables
        fs_args (dict): A dictionary of arguments to pass to the filesystem initializer

    Returns:
        dict: The artifact node message
    """

    uri = artifact_node_message["location"]["uri"]
    parsed_uri = urlparse(uri)
    fs = fsspec.filesystem(parsed_uri.scheme, **fs_args)

    parent_path, _ = os.path.split(parsed_uri.path)
    parent_uri = urlunparse(
        (parsed_uri.scheme, parsed_uri.netloc, parent_path, parsed_uri.params, parsed_uri.query, parsed_uri.fragment)
    )
    if not fs.exists(parent_uri):
        fs.makedirs(parent_uri)

    with fs.open(uri, "wb") as sink:
        writer = pa.RecordBatchFileWriter(sink, schema)
        for table in tables:
            writer.write_table(table)
        writer.close()

    return artifact_node_message
