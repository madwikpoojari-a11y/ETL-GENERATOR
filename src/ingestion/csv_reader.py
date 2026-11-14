"""
csv_reader.py  —  Ingestion Layer
----------------------------------
Reads a CSV file (from a file path or a Streamlit UploadedFile object)
and returns a raw pandas DataFrame plus file metadata.

No cleaning happens here. This module's only job is to get the data
into memory reliably and report basic facts about the file.
"""

import pandas as pd
import os
import io
from src.utils.logger import get_logger

logger = get_logger(__name__)


def read_csv(source) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame.

    Input:
        source — either:
            • a string file path  (e.g. "data/dirty_data.csv")
            • a Streamlit UploadedFile object

    Output:
        pd.DataFrame — raw, unmodified data from the CSV

    Raises:
        ValueError  if the file is empty or cannot be parsed
        FileNotFoundError  if a path is given and the file does not exist
    """
    logger.info("Reading CSV source: %s", getattr(source, "name", source))

    try:
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"File not found: {source}")
            df = pd.read_csv(source, dtype=str, keep_default_na=True)
        else:
            # Streamlit UploadedFile — read bytes, wrap in StringIO
            bytes_data = source.read()
            df = pd.read_csv(io.StringIO(bytes_data.decode("utf-8")),
                             dtype=str, keep_default_na=True)

        if df.empty:
            raise ValueError("The uploaded CSV file contains no data.")

        logger.info(
            "CSV loaded successfully: %d rows x %d columns",
            df.shape[0], df.shape[1]
        )
        return df

    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty.")
        raise ValueError("The CSV file is empty.")
    except pd.errors.ParserError as e:
        logger.error("CSV parse error: %s", str(e))
        raise ValueError(f"Could not parse CSV: {e}")


def get_metadata(source) -> dict:
    """
    Returns basic metadata about the CSV file without loading it fully.

    Input:
        source — file path string or Streamlit UploadedFile

    Output:
        dict with keys:
            file_name     (str)
            file_size_kb  (float)
            row_count     (int)
            column_count  (int)
            columns       (list of str)
    """
    df = read_csv(source)

    if isinstance(source, str):
        file_name = os.path.basename(source)
        file_size_kb = round(os.path.getsize(source) / 1024, 2)
    else:
        file_name = getattr(source, "name", "uploaded_file.csv")
        file_size_kb = round(len(source.getvalue()) / 1024, 2)

    metadata = {
        "file_name":    file_name,
        "file_size_kb": file_size_kb,
        "row_count":    df.shape[0],
        "column_count": df.shape[1],
        "columns":      list(df.columns),
    }

    logger.info("Metadata: %s", metadata)
    return metadata
