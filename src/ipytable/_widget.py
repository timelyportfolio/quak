from __future__ import annotations

import pathlib
import typing

import anywidget
import anywidget.experimental
import duckdb
import traitlets

DataFrameObject = typing.Any

if typing.TYPE_CHECKING:
    import pyarrow as pa


# Copied from Altair
# https://github.com/vega/altair/blob/18a2c3c237014591d172284560546a2f0ac1a883/altair/utils/data.py#L343
def arrow_table_from_dataframe_protocol(dflike: DataFrameObject) -> pa.lib.Table:
    """Convert a DataFrame-like object to a pyarrow Table."""
    import pyarrow as pa
    import pyarrow.interchange as pi

    # First check if the dataframe object has a method to convert to arrow.
    # Give this preference over the pyarrow from_dataframe function
    # since the object
    # has more control over the conversion, and may have broader compatibility.
    # This is the case for Polars, which supports Date32 columns in
    # direct conversion
    # while pyarrow does not yet support this type in from_dataframe
    for convert_method_name in ("arrow", "to_arrow", "to_arrow_table"):
        convert_method = getattr(dflike, convert_method_name, None)
        if callable(convert_method):
            result = convert_method()
            if isinstance(result, pa.Table):
                return result

    return pi.from_dataframe(dflike)  # type: ignore[no-any-return]


def table_to_ipc(table: pa.lib.Table) -> memoryview:
    """Convert a pyarrow Table to an Arrow IPC message."""
    import io

    import pyarrow.feather as feather

    sink = io.BytesIO()
    feather.write_feather(table, sink, compression="uncompressed")
    return sink.getbuffer()


def record_batch_to_ipc(record_batch: pa.lib.RecordBatch) -> memoryview:
    import pyarrow as pa

    table = pa.Table.from_batches([record_batch], schema=record_batch.schema)
    return table_to_ipc(table)


class Widget(anywidget.AnyWidget):
    """An anywidget for displaying tabular data in a table."""

    _esm = pathlib.Path(__file__).parent / "widget.js"
    _table_name = traitlets.Unicode("df").tag(sync=True)

    def __init__(self, df=None, *, conn=None, table_name: None | str = None):
        if conn is None:
            conn = duckdb.connect(":memory:")
            if df is None:
                assert table_name is not None, "Must provide a table name if no df"
            else:
                table_name = "df"
                conn.register("df", arrow_table_from_dataframe_protocol(df))
        self._conn = conn
        self._reader = None
        self._rows_per_batch = 256
        super().__init__(_table_name=table_name)

    @anywidget.experimental.command
    def _execute(self, msg: dict, buffers: list[bytes]):
        print(msg["sql"])
        result = self._conn.execute(msg["sql"])
        self._reader = result.fetch_record_batch(self._rows_per_batch)
        try:
            record_batch = self._reader.read_next_batch()
            ipc = record_batch_to_ipc(record_batch)
            return False, [ipc.tobytes()]
        except StopIteration:
            # No rows, but we need to return a schema
            ipc = table_to_ipc(self._reader.schema.empty_table())
            return True, [ipc.tobytes()]

    @anywidget.experimental.command
    def _next_batch(self, msg: dict, buffers: list[bytes]):
        print("next batch")
        if self._reader is None:
            return True, []
        try:
            record_batch = self._reader.read_next_batch()
            ipc = record_batch_to_ipc(record_batch)
            return False, [ipc.tobytes()]
        except StopIteration:
            ipc = table_to_ipc(self._reader.schema.empty_table())
            self._reader = None
            return True, [ipc.tobytes()]
